from pathlib import Path
import sys, pandas as pd
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "data" / "news"
SENT = ROOT / "data" / "sentiment"

def analyze_file(date_str: str):
    from textblob import TextBlob
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    vader = SentimentIntensityAnalyzer()
    f = NEWS / f"crypto_news_{date_str}.csv"
    if not f.exists():
        print("missing news file")
        return
    df = pd.read_csv(f)
    rows = []
    for _, r in df.iterrows():
        full = f"{r.get('headline','')} {r.get('summary','')}"
        v = vader.polarity_scores(full)["compound"]
        tb = TextBlob(full).sentiment.polarity
        score = 0.6*v + 0.4*tb
        rows.append({
            "time": r["time"],
            "headline": r["headline"],
            "sentiment": 1 if score > 0.03 else (-1 if score < -0.03 else 0),
            "confidence": min(abs(score), 1.0),
            "score": score
        })
    out = pd.DataFrame(rows).sort_values("time", ascending=False)
    SENT.mkdir(parents=True, exist_ok=True)
    out.to_csv(SENT / f"sentiment_analysis_{date_str}.csv", index=False)
    print(f"backfilled -> sentiment_analysis_{date_str}.csv")

if __name__ == "__main__":
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    analyze_file(date_str)
