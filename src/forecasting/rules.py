from dataclasses import dataclass
import pandas as pd

@dataclass
class Thresholds:
    sentiment: float = 0.03
    momentum: float = 0.02

@dataclass
class PredictCfg:
    lookback_minutes: int = 60
    min_articles: int = 3

def classify(x: float, th: float) -> int:
    return 1 if x > th else (-1 if x < -th else 0)

def direction_and_confidence(df: pd.DataFrame, th: Thresholds, pcfg: PredictCfg) -> tuple[str, float, dict]:
    if df is None or df.empty or "datetime" not in df or "sentiment" not in df or "confidence" not in df:
        return "NEUTRAL", 0.5, {}

    df = df.sort_values("datetime").copy()
    df["weighted"] = df["sentiment"] * df["confidence"]

    now = df["datetime"].max()
    cut = now - pd.Timedelta(minutes=pcfg.lookback_minutes)
    recent = df[df["datetime"] >= cut]
    daily = df

    r_avg = recent["weighted"].mean() if not recent.empty else 0.0
    d_avg = daily["weighted"].mean() if not daily.empty else 0.0
    momentum = r_avg - d_avg

    cls = recent["weighted"].apply(lambda x: classify(x, th.sentiment)) if not recent.empty else pd.Series(dtype=int)
    pos = int((cls == 1).sum()); neg = int((cls == -1).sum())
    ratio = (pos - neg) / (pos + neg) if (pos + neg) > 0 else 0.0

    if len(recent) < pcfg.min_articles:
        direction = "NEUTRAL"
    elif abs(momentum) < th.momentum:
        direction = "UP" if ratio > 0.3 else ("DOWN" if ratio < -0.3 else "NEUTRAL")
    else:
        direction = "UP" if momentum > 0 else "DOWN"

    vol = min(len(recent) / 10.0, 1.0)
    strength = min(abs(r_avg) * 2, 1.0)
    mom = min(abs(momentum) * 5, 1.0)
    confidence = min(0.95, 0.4 * vol + 0.3 * strength + 0.3 * mom)

    extras = {
        "recent_avg": r_avg,
        "daily_avg": d_avg,
        "momentum": momentum,
        "pos_neg_ratio": ratio,
        "n_recent": len(recent),
    }
    return direction, float(confidence), extras
