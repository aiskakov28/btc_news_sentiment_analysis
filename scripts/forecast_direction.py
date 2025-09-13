from pathlib import Path
from datetime import datetime, timedelta
import yaml, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "model.yaml"
DATA = ROOT / "data" / "sentiment"

with open(CFG) as f:
    cfg = yaml.safe_load(f)

DATE = datetime.now().strftime("%Y-%m-%d")
FILE = DATA / f"sentiment_analysis_{DATE}.csv"

def classify(x, th):
    return 1 if x > th else (-1 if x < -th else 0)

def main():
    if not FILE.exists():
        print("NEUTRAL 0.5")
        return
    df = pd.read_csv(FILE)
    df["datetime"] = pd.to_datetime(DATE + " " + df["time"])
    df["weighted"] = df["sentiment"] * df["confidence"]

    now = df["datetime"].max()
    recent_cut = now - timedelta(minutes=cfg["prediction"]["lookback_minutes"])
    recent = df[df["datetime"] >= recent_cut]
    daily = df

    r_avg = (recent["weighted"].mean() if not recent.empty else 0.0)
    d_avg = (daily["weighted"].mean() if not daily.empty else 0.0)
    momentum = r_avg - d_avg

    th = cfg["thresholds"]["sentiment"]
    cls = recent["weighted"].apply(lambda x: classify(x, th)) if not recent.empty else pd.Series(dtype=int)
    pos = int((cls == 1).sum()); neg = int((cls == -1).sum())
    ratio = (pos - neg) / (pos + neg) if (pos + neg) > 0 else 0.0

    if len(recent) < cfg["prediction"]["min_articles"]:
        direction = "NEUTRAL"
    elif abs(momentum) < cfg["thresholds"]["momentum"]:
        direction = "UP" if ratio > 0.3 else ("DOWN" if ratio < -0.3 else "NEUTRAL")
    else:
        direction = "UP" if momentum > 0 else "DOWN"

    vol = min(len(recent) / 10.0, 1.0)
    strength = min(abs(r_avg) * 2, 1.0)
    mom = min(abs(momentum) * 5, 1.0)
    conf = min(0.95, 0.4*vol + 0.3*strength + 0.3*mom)

    print(f"{direction} {conf:.2f}")

if __name__ == "__main__":
    main()
