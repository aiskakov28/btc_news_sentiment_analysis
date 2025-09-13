import pandas as pd

def resample_mean(df: pd.DataFrame, value_col: str, rule: str) -> pd.DataFrame:
    return (
        df.set_index("datetime")[[value_col]]
          .resample(rule).mean()
          .dropna()
          .reset_index()
    )

def rolling_mean(df: pd.DataFrame, value_col: str, window: int) -> pd.Series:
    return df[value_col].rolling(max(1, window)).mean()

def recent_window(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    if df.empty:
        return df
    end = df["datetime"].max()
    start = end - pd.Timedelta(minutes=minutes)
    return df[(df["datetime"] >= start) & (df["datetime"] <= end)]

def pos_neg_ratio(series: pd.Series, threshold: float) -> float:
    cls = series.apply(lambda x: 1 if x > threshold else (-1 if x < -threshold else 0))
    pos = (cls == 1).sum()
    neg = (cls == -1).sum()
    return (pos - neg) / (pos + neg) if (pos + neg) > 0 else 0.0
