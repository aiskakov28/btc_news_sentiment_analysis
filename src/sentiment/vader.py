from functools import lru_cache
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

@lru_cache(maxsize=1)
def _analyzer() -> SentimentIntensityAnalyzer:
    return SentimentIntensityAnalyzer()

def score(text: str) -> float:
    return _analyzer().polarity_scores(text or "")["compound"]
