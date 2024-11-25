# btc_news_sentiment_analysis
## Overview

A real-time sentiment analysis system that predicts Bitcoin price movements by analyzing cryptocurrency news from multiple sources. The project combines natural language processing techniques with market-specific indicators to generate directional predictions with confidence scores.

## Key Features:

- Real-time news collection from 14 major cryptocurrency news sources
- Multi-layered sentiment analysis using VADER, TextBlob, and custom market indicators
- Hourly price direction predictions with confidence scoring
- Automated data collection and cleaning pipeline

## Technical Architecture

The project consists of three main components:

### 1. News Collection (finance_news.py):

- Collects news from multiple RSS feeds every 5 minutes
- Implements automatic deduplication and data cleaning
- Generates daily summaries and maintains a 30-day rolling window of historical data

### 2. Sentiment Analysis (finance_sent.py):

- Hybrid sentiment analysis combining:
- VADER sentiment analysis for crypto-specific context
- TextBlob for additional polarity detection
- Custom market indicator dictionary with over 500 categorized terms
- Weighted scoring system with confidence thresholds

### 3. Price Direction Prediction ([forecast.py](http://forecast.py)):

- Analyzes sentiment trends over configurable time windows
- Calculates sentiment momentum and market consensus
- Generates UP/DOWN/NEUTRAL predictions with confidence scores
- Considers multiple factors including volume, strength, ratio, and momentum

## Dependencies:

```
pandas
numpy
feedparser
textblob
vaderSentiment
pytz
```

## Project Structure:

```
project/
├── data/
│   ├── news/
│   └── sentiment/
├── logs/
├── finance_news.py
├── finance_sent.py
└── forecast.py
```

## Usage:

1. Start the news collector:

```bash
python finance_news.py
```

1. Run sentiment analysis:

```bash
python finance_sent.py
```

1. Generate predictions:

```bash
python forecast.py
```

## Output Format:

The system generates predictions in the following format:

```
Direction: UP/DOWN/NEUTRAL
Confidence: 0.0-1.0 (95% maximum)
```

## Performance Considerations:

- News collection occurs every 5 minutes to ensure timely data
- Sentiment analysis uses weighted scoring to reduce false positives
- Minimum article threshold (3) required for valid predictions
- Confidence scores are adjusted based on market consensus

## Future Improvements:

- Integration with real-time price data for validation
- Machine learning model for adaptive sentiment weighting
- Additional news sources and social media integration
- API endpoint for real-time predictions
