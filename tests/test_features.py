import pandas as pd
from datetime import datetime, timedelta
from src.features.time_windows import resample_mean, rolling_mean, recent_window, pos_neg_ratio

def _series():
    base = datetime(2024,1,1,12,0,0)
    dt = [base + timedelta(minutes=5*i) for i in range(12)]
    return pd.DataFrame({"datetime": dt, "v": list(range(12))})

def test_resample_and_rolling():
    df = _series()
    rs = resample_mean(df.rename(columns={"v":"value"}), "value", "15min")
    assert not rs.empty
    roll = rolling_mean(df, "v", 3)
    assert len(roll) == len(df)

def test_recent_and_ratio():
    df = _series()
    r = recent_window(df, 20)
    assert r["datetime"].max() - r["datetime"].min() <= pd.Timedelta(minutes=20)
    s = pd.Series([0.1, 0.2, -0.5, 0.0, 0.3])
    ratio = pos_neg_ratio(s, 0.05)
    assert -1.0 <= ratio <= 1.0
