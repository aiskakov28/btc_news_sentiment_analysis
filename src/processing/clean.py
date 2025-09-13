from datetime import datetime
import pandas as pd

TZ = datetime.now().astimezone().tzinfo

def normalize_news(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["date","time","headline","source","link","summary"]
    df = df[cols].copy()
    df["headline"] = df["headline"].fillna("").str.strip()
    df["summary"] = df["summary"].fillna("").str.strip()
    df["source"] = df["source"].fillna("").str.lower()
    df["link"] = df["link"].fillna("")
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"]).dt.tz_localize(TZ, nonexistent="NaT", ambiguous="NaT")
    df = df.dropna(subset=["headline"]).drop_duplicates(subset=["headline"])
    return df.sort_values("datetime", ascending=False)

def normalize_sentiment(df: pd.DataFrame, date_str: str) -> pd.DataFrame:
    cols = ["time","headline","sentiment","confidence"]
    df = df[cols].copy()
    df["headline"] = df["headline"].fillna("").str.strip()
    df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce").fillna(0).astype(int)
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.0).clip(0, 1)
    df["datetime"] = pd.to_datetime(date_str + " " + df["time"]).dt.tz_localize(TZ, nonexistent="NaT", ambiguous="NaT")
    return df.dropna(subset=["datetime"]).sort_values("datetime")
