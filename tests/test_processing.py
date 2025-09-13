import pandas as pd
from src.processing.clean import normalize_news, normalize_sentiment

def test_normalize_news():
    df = pd.DataFrame([
        {"date":"2024-01-01","time":"12:00:00","headline":"A","source":"X","link":"u","summary":"s"},
        {"date":"2024-01-01","time":"12:05:00","headline":"A","source":"X","link":"u2","summary":"s2"},
    ])
    out = normalize_news(df)
    assert out["headline"].nunique() == 1
    assert "datetime" in out.columns

def test_normalize_sentiment():
    df = pd.DataFrame([
        {"time":"12:00:00","headline":"A","sentiment":1,"confidence":0.4},
        {"time":"12:10:00","headline":"B","sentiment":-1,"confidence":1.2},
    ])
    out = normalize_sentiment(df, "2024-01-01")
    assert out["confidence"].max() <= 1.0
    assert set(out["sentiment"].unique()).issubset({-1,0,1})
