import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import pytz

# Get local timezone
local_tz = datetime.now().astimezone().tzinfo

# Get project root and configure paths
PROJECT_ROOT = Path(__file__).parent
CRYPTO_NEWS_DIR = PROJECT_ROOT / "data/news"
SENTIMENT_DIR = PROJECT_ROOT / "data/sentiment"
LOG_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
CRYPTO_NEWS_DIR.mkdir(parents=True, exist_ok=True)
SENTIMENT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_DIR / 'sentiment_analyzer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NewsAnalyzer:
    def __init__(self):
        self.news_dir = CRYPTO_NEWS_DIR
        self.output_dir = SENTIMENT_DIR
        self.vader = SentimentIntensityAnalyzer()
        print(f"News directory: {self.news_dir}")
        print(f"Output directory: {self.output_dir}")

        # Further expanded market indicators with additional terms
        self.market_indicators = {
            'strong_positive': [
                # Original terms (keeping all existing terms)
                'breakthrough', 'surge', 'skyrocket', 'outperform', 'record high',
                'stellar', 'explosive growth', 'soar', 'rocket', 'moonshot',
                'milestone', 'triumph', 'revolutionary', 'game-changing',
                'unprecedented gains', 'massive adoption', 'extraordinary growth',
                'spectacular rise', 'phenomenal', 'exceptional performance',
                'dominant', 'leading', 'innovative breakthrough', 'major victory',
                'groundbreaking', 'remarkable success', 'outstanding',
                'all-time high', 'historic peak', 'exponential growth',
                'massive success', 'incredible achievement', 'tremendous success',
                'market leader', 'industry pioneer', 'transformative innovation',
                'breakthrough technology', 'market dominance', 'overwhelming success',
                'exceptional results', 'extraordinary success', 'remarkable growth',
                'unprecedented success', 'massive breakthrough', 'major milestone',
                'significant advancement', 'revolutionary development',
                # First expansion (keeping all existing additional terms)
                'record-breaking performance', 'unprecedented achievement',
                'extraordinary advancement', 'remarkable breakthrough',
                'historic achievement', 'exceptional milestone',
                'outstanding success', 'phenomenal growth',
                'monumental success', 'breakthrough innovation',
                'market-leading performance', 'revolutionary breakthrough',
                'extraordinary milestone', 'remarkable advancement',
                'unprecedented milestone', 'extraordinary achievement',
                'exceptional breakthrough', 'transformative success',
                'revolutionary success', 'historic breakthrough',
                'massive transformation', 'exceptional innovation',
                'extraordinary development', 'revolutionary milestone',
                'breakthrough achievement', 'transformative milestone',
                'historic transformation', 'exceptional advancement',
                'revolutionary transformation', 'breakthrough success',
                'transformative advancement', 'historic innovation',
                'revolutionary achievement', 'breakthrough development',
                'transformative breakthrough', 'historic success',
                'revolutionary advancement', 'breakthrough transformation',
                'transformative development', 'historic milestone',
                'revolutionary development', 'breakthrough milestone',
                # Second expansion (new terms)
                'paradigm shift', 'market revolution', 'industry disruption',
                'phenomenal breakthrough', 'extraordinary triumph',
                'unprecedented excellence', 'transformative victory',
                'revolutionary innovation', 'exceptional dominance',
                'historic transformation', 'remarkable revolution',
                'breakthrough leadership', 'market transformation',
                'industry breakthrough', 'transformative excellence',
                'revolutionary triumph', 'exceptional revolution',
                'historic innovation', 'remarkable transformation',
                'breakthrough excellence'
            ],

            'positive': [
                # Original terms (keeping all existing terms)
                'rise', 'gain', 'climb', 'rally', 'boost', 'growth', 'profit',
                'success', 'adoption', 'bullish', 'upward', 'advance', 'improve',
                'strengthen', 'recover', 'upgrade', 'progress', 'momentum',
                'optimistic', 'confident', 'promising', 'favorable', 'advantage',
                'beneficial', 'opportunity', 'potential', 'thrive', 'prosper',
                'achievement', 'positive outlook', 'bright future', 'endorsement',
                'support', 'backing', 'partnership', 'collaboration',
                'expansion', 'development', 'enhancement', 'advancement',
                'appreciation', 'improvement', 'progression', 'acceleration',
                'stabilization', 'recovery', 'rebound', 'upturn', 'upswing',
                'positive momentum', 'market confidence', 'investor interest',
                'strategic alliance', 'successful implementation', 'positive trend',
                'market acceptance', 'growing demand', 'increased adoption',
                'positive sentiment', 'market optimism', 'strong performance',
                # First expansion (keeping all existing additional terms)
                'upward trend', 'positive development', 'market strength',
                'increasing value', 'steady growth', 'positive progress',
                'market improvement', 'growing interest', 'positive direction',
                'market opportunity', 'favorable trend', 'positive momentum',
                'market progress', 'steady improvement', 'positive movement',
                'market advancement', 'favorable development', 'positive trajectory',
                'market potential', 'steady progress', 'positive outlook',
                'market growth', 'favorable position', 'positive indication',
                'market success', 'steady advancement', 'positive signal',
                'market stability', 'favorable outlook', 'positive development',
                'market recovery', 'steady momentum', 'positive atmosphere',
                'market appreciation', 'favorable condition', 'positive environment',
                'market strength', 'steady progression', 'positive climate',
                'market improvement', 'favorable situation', 'positive landscape',
                'market advance', 'steady development', 'positive territory',
                'market uptick', 'favorable momentum', 'positive direction',
                'market progress', 'steady improvement', 'positive trend',
                # Second expansion (new terms)
                'constructive development', 'encouraging progress',
                'healthy growth', 'sustainable advance',
                'robust performance', 'solid gains',
                'steady appreciation', 'positive trajectory',
                'forward momentum', 'favorable dynamics',
                'upward mobility', 'progressive growth',
                'positive evolution', 'advantageous position',
                'beneficial trend', 'promising outlook',
                'optimistic direction', 'favorable progress',
                'positive momentum', 'constructive trend'
            ],

            'strong_negative': [
                # Original terms (keeping all existing terms)
                'crash', 'plunge', 'collapse', 'disaster', 'crisis', 'bankruptcy',
                'scandal', 'hack', 'scam', 'breach', 'exploit', 'attack', 'dump',
                'manipulation', 'fraud', 'investigation', 'sec', 'lawsuit',
                'criminal', 'catastrophic', 'devastating', 'severe', 'emergency',
                'critical failure', 'massive selloff', 'market crash',
                'security breach', 'major hack', 'ponzi scheme', 'money laundering',
                'regulatory crackdown', 'banned', 'blacklisted', 'shut down',
                'forced liquidation', 'margin call', 'flash crash', 'market manipulation',
                'insider trading', 'illegal activity', 'cyber attack', 'system failure',
                'technical disaster', 'complete breakdown', 'market meltdown',
                'severe downturn', 'major crisis', 'devastating loss',
                'catastrophic failure', 'total collapse', 'massive fraud',
                'critical breach', 'severe attack', 'major scandal',
                'regulatory enforcement', 'criminal charges', 'serious violation',
                'emergency shutdown', 'critical vulnerability', 'massive exodus',
                'severe breach', 'major exploitation', 'systemic failure',
                # First expansion (keeping all existing additional terms)
                'market catastrophe', 'devastating collapse', 'extreme crisis',
                'major breakdown', 'severe crash', 'critical meltdown',
                'massive default', 'catastrophic breach', 'extreme failure',
                'major disaster', 'severe crisis', 'critical collapse',
                'massive breakdown', 'catastrophic crash', 'extreme meltdown',
                'major breach', 'severe disaster', 'critical crisis',
                'massive collapse', 'catastrophic meltdown', 'extreme disaster',
                'major crisis', 'severe breakdown', 'critical disaster',
                'massive crisis', 'catastrophic disaster', 'extreme breakdown',
                'major meltdown', 'severe collapse', 'critical breakdown',
                'massive disaster', 'catastrophic breakdown', 'extreme collapse',
                'major collapse', 'severe meltdown', 'critical attack',
                'massive meltdown', 'catastrophic attack', 'extreme attack',
                'major attack', 'severe attack', 'fatal error',
                'devastating attack', 'catastrophic error', 'extreme error',
                'major error', 'severe error', 'critical error',
                # Second expansion (new terms)
                'market implosion', 'devastating catastrophe',
                'total meltdown', 'systemic collapse',
                'extreme breakdown', 'critical disaster',
                'massive crisis', 'catastrophic failure',
                'complete destruction', 'devastating crash',
                'market destruction', 'fatal collapse',
                'severe catastrophe', 'critical implosion',
                'extreme devastation', 'massive destruction',
                'total devastation', 'catastrophic crisis',
                'severe disaster', 'critical catastrophe'
            ],

            'negative': [
                # Original terms (keeping all existing terms)
                'drop', 'fall', 'decline', 'loss', 'risk', 'bearish', 'downward',
                'concern', 'volatile', 'uncertainty', 'warning', 'threat', 'suspend',
                'halt', 'delay', 'pressure', 'weak', 'selling', 'correction', 'fear',
                'worried', 'anxious', 'nervous', 'cautious', 'skeptical', 'doubt',
                'problem', 'issue', 'trouble', 'difficult', 'challenging', 'struggle',
                'setback', 'obstacle', 'barrier', 'restriction', 'limitation',
                'vulnerability', 'exposure', 'risky', 'dangerous', 'unstable',
                'unreliable', 'controversial', 'questionable', 'suspicious',
                'red flag', 'concern', 'worried', 'pessimistic', 'negative outlook',
                'market weakness', 'decreased value', 'poor performance',
                'declining interest', 'market pressure', 'reduced confidence',
                'negative trend', 'market anxiety', 'investor concern',
                'troubling development', 'adverse effect', 'negative impact',
                'growing concerns', 'market tension', 'increasing pressure',
                'deteriorating conditions', 'unfavorable outlook', 'mounting pressure',
                # First expansion (keeping all existing additional terms)
                'weakening', 'deterioration', 'instability', 'uncertainty',
                'market stress', 'negative sentiment', 'market weakness',
                'declining trend', 'adverse trend', 'market pressure',
                'negative direction', 'market concern', 'declining momentum',
                'adverse development', 'market tension', 'negative movement',
                'market worry', 'declining situation', 'adverse condition',
                'market difficulty', 'negative progression', 'market trouble',
                'declining position', 'adverse circumstance', 'market problem',
                'negative situation', 'market difficulty', 'declining state',
                'adverse position', 'market challenge', 'negative state',
                'market issue', 'declining condition', 'adverse situation',
                'market setback', 'negative condition', 'market decline',
                'declining environment', 'adverse climate', 'market downturn',
                'negative environment', 'market slide', 'declining atmosphere',
                'adverse trend', 'market dip', 'negative atmosphere',
                # Second expansion (new terms)
                'subdued performance', 'challenging environment',
                'unfavorable trend', 'worrying development',
                'concerning situation', 'troubled outlook',
                'downward pressure', 'negative trajectory',
                'weakening position', 'deteriorating outlook',
                'adverse momentum', 'declining prospects',
                'negative direction', 'troubling trend',
                'market headwind', 'concerning development',
                'negative progression', 'weakening trend',
                'adverse direction', 'troubled development'
            ],

            'neutral': [
                # Original terms (keeping all existing terms)
                'stable', 'steady', 'unchanged', 'maintain', 'hold', 'consolidate',
                'range-bound', 'sideways', 'balanced', 'consistent', 'regular',
                'normal', 'standard', 'typical', 'expected', 'anticipated',
                'in line', 'as predicted', 'moderate', 'average', 'middle ground',
                'status quo', 'equilibrium', 'stabilize', 'level off', 'plateau',
                'remain', 'continue', 'persist', 'sustain', 'flat',
                'constant', 'settled', 'stationary', 'neutral trend',
                'market stability', 'steady state', 'baseline performance',
                'standard operation', 'usual activity', 'normal trading',
                'market equilibrium', 'stable condition', 'ordinary level',
                'expected range', 'typical pattern', 'regular movement',
                'sustained level', 'maintained position', 'steady progress',
                # First expansion (keeping all existing additional terms)
                'balanced market', 'neutral position', 'steady state',
                'stable condition', 'normal range', 'typical level',
                'expected pattern', 'regular trend', 'sustained position',
                'maintained level', 'steady situation', 'balanced condition',
                'neutral state', 'steady pattern', 'stable trend',
                'normal position', 'typical situation', 'expected movement',
                'regular pattern', 'sustained trend', 'maintained situation',
                'steady development', 'balanced trend', 'neutral pattern',
                'steady movement', 'stable pattern', 'normal trend',
                'typical movement', 'expected condition', 'regular state',
                'sustained movement', 'maintained pattern', 'steady level',
                'balanced state', 'neutral movement', 'steady condition',
                'stable movement', 'normal pattern', 'typical state',
                'expected situation', 'regular position', 'sustained state',
                # Second expansion (new terms)
                'measured performance', 'consistent trend',
                'stable progression', 'balanced development',
                'steady evolution', 'neutral trajectory',
                'maintained equilibrium', 'stable dynamics',
                'balanced momentum', 'steady course',
                'neutral direction', 'stable path',
                'balanced progress', 'steady flow',
                'neutral development', 'stable rhythm',
                'balanced movement', 'steady pace',
                'neutral progression', 'stable motion'
            ]
        }

    def get_market_sentiment_score(self, text):
        text_lower = text.lower()
        scores = {
            'strong_positive': sum(text_lower.count(term) for term in self.market_indicators['strong_positive']) * 1.5,
            'positive': sum(text_lower.count(term) for term in self.market_indicators['positive']),
            'strong_negative': sum(text_lower.count(term) for term in self.market_indicators['strong_negative']) * -2.5,
            'negative': sum(text_lower.count(term) for term in self.market_indicators['negative']) * -1.5,
            'neutral': sum(text_lower.count(term) for term in self.market_indicators['neutral']) * 0.5
        }

        if scores['strong_negative'] + scores['negative'] < -2:
            scores['negative'] *= 1.2
        return sum(scores.values())

    def get_enhanced_sentiment(self, headline, summary, confidence_threshold=0.2):
        full_text = f"{headline} {summary}"

        vader_scores = {
            'headline': self.vader.polarity_scores(headline),
            'summary': self.vader.polarity_scores(summary),
            'full': self.vader.polarity_scores(full_text)
        }

        textblob_scores = {
            'headline': TextBlob(headline).sentiment.polarity,
            'summary': TextBlob(summary).sentiment.polarity,
            'full': TextBlob(full_text).sentiment.polarity
        }

        market_score = self.get_market_sentiment_score(full_text)

        combined_score = (
                vader_scores['headline']['compound'] * 0.25 +
                vader_scores['summary']['compound'] * 0.25 +
                textblob_scores['headline'] * 0.15 +
                textblob_scores['summary'] * 0.15 +
                market_score * 0.2
        )

        if combined_score > 0:
            combined_score *= 0.8
        else:
            combined_score *= 1.2

        confidence = abs(combined_score)

        if confidence < confidence_threshold:
            sentiment = 0
        else:
            sentiment = 1 if combined_score > 0.25 else (-1 if combined_score < -0.15 else 0)

        return sentiment, confidence, {
            'vader': vader_scores,
            'textblob': textblob_scores,
            'market': market_score
        }

    def analyze_daily_sentiment(self):
        current_date = datetime.now(local_tz).strftime("%Y-%m-%d")
        logging.info(f"Starting analysis for {current_date}")

        try:
            news_file = self.news_dir / f"crypto_news_{current_date}.csv"
            print(f"Looking for news file: {news_file}")

            if not news_file.exists():
                raise FileNotFoundError(f"News file not found: {news_file}")

            df = pd.read_csv(news_file)
            logging.info(f"Loaded {len(df)} articles from {news_file}")

            results = []
            for idx, row in df.iterrows():
                logging.info(f"Processing article {idx + 1}/{len(df)}")
                sentiment, confidence, details = self.get_enhanced_sentiment(
                    row['headline'],
                    row['summary']
                )
                results.append({
                    'time': row['time'],
                    'headline': row['headline'],
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'details': details
                })

            results_df = pd.DataFrame(results)

            # Save results
            output_file = self.output_dir / f"sentiment_analysis_{current_date}.csv"
            results_df.to_csv(output_file, index=False)
            logging.info(f"Results saved to {output_file}")

            # Calculate statistics
            high_conf_results = results_df[results_df['confidence'] >= 0.2]
            sentiment_counts = {
                'Positive': len(high_conf_results[high_conf_results['sentiment'] == 1]),
                'Neutral': len(results_df[results_df['confidence'] < 0.2]) +
                           len(high_conf_results[high_conf_results['sentiment'] == 0]),
                'Negative': len(high_conf_results[high_conf_results['sentiment'] == -1])
            }

            total = len(results_df)
            summary = f"\nSentiment Analysis Summary for {current_date}:\n"
            summary += f"Total articles analyzed: {total}\n"
            summary += f"Positive articles: {sentiment_counts['Positive']} ({(sentiment_counts['Positive'] / total) * 100:.1f}%)\n"
            summary += f"Neutral articles: {sentiment_counts['Neutral']} ({(sentiment_counts['Neutral'] / total) * 100:.1f}%)\n"
            summary += f"Negative articles: {sentiment_counts['Negative']} ({(sentiment_counts['Negative'] / total) * 100:.1f}%)\n"

            print(summary)
            logging.info(summary)

        except Exception as e:
            error_msg = f"Error analyzing news: {str(e)}"
            logging.error(error_msg)
            print(error_msg)


if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    analyzer.analyze_daily_sentiment()