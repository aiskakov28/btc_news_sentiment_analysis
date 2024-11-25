import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import os

# Get local timezone and configure paths
local_tz = datetime.now().astimezone().tzinfo
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"


class SentimentPredictor:
    def __init__(self, lookback_minutes=60):
        self.lookback_minutes = lookback_minutes
        self.sentiment_threshold = 0.03
        self.momentum_threshold = 0.02
        self.min_articles = 3
        self.confidence_weights = {
            'momentum': 0.3,
            'strength': 0.2,
            'ratio': 0.3,
            'volume': 0.2
        }

    def load_sentiment_data(self, current_date):
        sentiment_file = DATA_DIR / "sentiment" / f"sentiment_analysis_{current_date}.csv"
        print(f"Looking for sentiment file: {sentiment_file}")

        if sentiment_file.exists():
            try:
                sentiment_data = pd.read_csv(sentiment_file)
                sentiment_data['datetime'] = pd.to_datetime(
                    current_date + ' ' + sentiment_data['time']
                ).dt.tz_localize(local_tz)
                sentiment_data['weighted_sentiment'] = sentiment_data['sentiment'] * sentiment_data['confidence']
                return sentiment_data
            except Exception as e:
                print(f"Error loading sentiment data: {str(e)}")
        return None

    def classify_sentiment(self, sentiment_score):
        if sentiment_score > self.sentiment_threshold:
            return 'positive'
        elif sentiment_score < -self.sentiment_threshold:
            return 'negative'
        else:
            return 'neutral'

    def calculate_confidence_score(self, recent_analysis, daily_analysis, sentiment_momentum):
        # Volume confidence (based on number of articles)
        max_expected_articles = 10  # Expected number of articles per hour
        volume_confidence = min(recent_analysis['total_articles'] / max_expected_articles, 1.0)

        # Strength confidence
        strength_ratio = recent_analysis['sentiment_strength'] / max(daily_analysis['sentiment_strength'], 0.001)
        strength_confidence = min(strength_ratio, 1.0)

        # Momentum confidence
        momentum_confidence = min(abs(sentiment_momentum) * 5, 1.0)

        # Ratio confidence
        ratio_confidence = abs(recent_analysis['sentiment_ratio'])

        # Weighted combination
        total_confidence = (
                self.confidence_weights['momentum'] * momentum_confidence +
                self.confidence_weights['strength'] * strength_confidence +
                self.confidence_weights['ratio'] * ratio_confidence +
                self.confidence_weights['volume'] * volume_confidence
        )

        # Scale confidence based on article count
        if recent_analysis['total_articles'] < self.min_articles:
            total_confidence *= (recent_analysis['total_articles'] / self.min_articles)

        # Adjust confidence based on consensus
        consensus_factor = 1.0
        if recent_analysis['total_articles'] >= self.min_articles:
            pos_ratio = recent_analysis['positive'] / recent_analysis['total_articles']
            neg_ratio = recent_analysis['negative'] / recent_analysis['total_articles']
            if max(pos_ratio, neg_ratio) > 0.6:  # Strong consensus
                consensus_factor = 1.2

        return min(total_confidence * consensus_factor, 0.95)

    def analyze_sentiment_period(self, sentiment_df, start_time, end_time):
        if sentiment_df is None:
            return self.get_empty_analysis()

        if start_time.tzinfo is None:
            start_time = start_time.astimezone(local_tz)
        if end_time.tzinfo is None:
            end_time = end_time.astimezone(local_tz)

        period_data = sentiment_df[
            (sentiment_df['datetime'] >= start_time) &
            (sentiment_df['datetime'] <= end_time)
            ]

        if period_data.empty:
            return self.get_empty_analysis()

        weighted_sentiment = np.average(
            period_data['sentiment'],
            weights=period_data['confidence']
        )

        classifications = period_data['weighted_sentiment'].apply(self.classify_sentiment)
        pos_count = sum(classifications == 'positive')
        neg_count = sum(classifications == 'negative')

        sentiment_ratio = 0
        if (pos_count + neg_count) > 0:
            sentiment_ratio = (pos_count - neg_count) / (pos_count + neg_count)

        sentiment_strength = np.abs(period_data['weighted_sentiment']).mean()
        sentiment_volatility = period_data['sentiment'].std()

        return {
            'total_articles': len(period_data),
            'positive': pos_count,
            'negative': neg_count,
            'neutral': sum(classifications == 'neutral'),
            'avg_sentiment': weighted_sentiment,
            'avg_confidence': period_data['confidence'].mean(),
            'sentiment_strength': sentiment_strength,
            'sentiment_ratio': sentiment_ratio,
            'sentiment_volatility': sentiment_volatility
        }

    def get_empty_analysis(self):
        return {
            'total_articles': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'avg_sentiment': 0,
            'avg_confidence': 0,
            'sentiment_strength': 0,
            'sentiment_ratio': 0,
            'sentiment_volatility': 0
        }

    def predict(self):
        try:
            current_time = datetime.now(local_tz)
            current_date = current_time.strftime('%Y-%m-%d')

            (DATA_DIR / "sentiment").mkdir(parents=True, exist_ok=True)

            sentiment_df = self.load_sentiment_data(current_date)
            if sentiment_df is None:
                return "NEUTRAL", 0.5

            day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            recent_cutoff = current_time - timedelta(minutes=self.lookback_minutes)

            daily_analysis = self.analyze_sentiment_period(sentiment_df, day_start, current_time)
            recent_analysis = self.analyze_sentiment_period(sentiment_df, recent_cutoff, current_time)

            sentiment_momentum = recent_analysis['avg_sentiment'] - daily_analysis['avg_sentiment']

            # Determine direction
            if recent_analysis['total_articles'] < self.min_articles:
                direction = "NEUTRAL"
            elif abs(sentiment_momentum) < self.momentum_threshold:
                if abs(recent_analysis['sentiment_ratio']) > 0.3:
                    direction = "UP" if recent_analysis['sentiment_ratio'] > 0 else "DOWN"
                else:
                    direction = "NEUTRAL"
            else:
                direction = "UP" if sentiment_momentum > 0 else "DOWN"

            # Calculate confidence
            confidence = self.calculate_confidence_score(recent_analysis, daily_analysis, sentiment_momentum)

            self._print_analysis(daily_analysis, recent_analysis, sentiment_momentum, direction, confidence)
            return direction, confidence

        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            return "NEUTRAL", 0.0

    def _print_analysis(self, daily_analysis, recent_analysis, momentum, direction, confidence):
        output = f"""
╔══════════════════════════════════════════════════════════════╗
║                 Bitcoin Sentiment Analysis                    ║
╠══════════════════════════════════════════════════════════════╣
║ Time: {datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}
║
║ Last Hour Analysis:
║ • Total Articles: {recent_analysis['total_articles']}
║ • Positive: {recent_analysis['positive']}
║ • Negative: {recent_analysis['negative']}
║ • Neutral: {recent_analysis['neutral']}
║ • Average Sentiment: {recent_analysis['avg_sentiment']:.3f}
║ • Sentiment Ratio: {recent_analysis['sentiment_ratio']:.3f}
║ • Sentiment Strength: {recent_analysis['sentiment_strength']:.3f}
║ • Average Confidence: {recent_analysis['avg_confidence']:.1%}
║
║ Full Day Analysis:
║ • Total Articles: {daily_analysis['total_articles']}
║ • Positive: {daily_analysis['positive']}
║ • Negative: {daily_analysis['negative']}
║ • Neutral: {daily_analysis['neutral']}
║ • Average Sentiment: {daily_analysis['avg_sentiment']:.3f}
║ • Sentiment Ratio: {daily_analysis['sentiment_ratio']:.3f}
║ • Sentiment Strength: {daily_analysis['sentiment_strength']:.3f}
║ • Average Confidence: {daily_analysis['avg_confidence']:.1%}
║
║ Sentiment Momentum: {momentum:.3f}
║
║ PREDICTION (Next Hour):
║ • Direction: {direction}
║ • Confidence: {confidence:.1%}
║
╚══════════════════════════════════════════════════════════════╝"""
        print(output)


if __name__ == "__main__":
    predictor = SentimentPredictor(lookback_minutes=60)
    direction, confidence = predictor.predict()