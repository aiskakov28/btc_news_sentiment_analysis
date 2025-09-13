from pathlib import Path
from datetime import datetime
import yaml, pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "model.yaml"
DATA = ROOT / "data"
NEWS = DATA / "news"
SENT = DATA / "sentiment"
SENT.mkdir(parents=True, exist_ok=True)

with open(CFG) as f:
    model_cfg = yaml.safe_load(f)

DATE = datetime.now().strftime("%Y-%m-%d")
NEWS_FILE = NEWS / f"crypto_news_{DATE}.csv"
OUT = SENT / f"sentiment_analysis_{DATE}.csv"

vader = SentimentIntensityAnalyzer()
lex_pos = ["surge","soar","record","breakthrough","bullish","rally"]
lex_neg = ["crash","plunge","hack","lawsuit","fraud","bearish"]

def lex_score(text: str) -> float:
    t = text.lower()
    p = sum(t.count(w) for w in lex_pos)
    n = sum(t.count(w) for w in lex_neg)
    return p*0.5 - n*0.8

def analyze_row(headline, summary):
    full = f"{headline} {summary}"
    v = vader.polarity_scores(full)["compound"]
    tb = TextBlob(full).sentiment.polarity
    lx = lex_score(full)
    w = model_cfg["weights"]
    score = v*w["vader"] + tb*w["textblob"] + lx*w["lexicon"]
    conf = min(abs(score), 1.0)
    sent = 1 if score > model_cfg["thresholds"]["sentiment"] else (-1 if score < -model_cfg["thresholds"]["sentiment"] else 0)
    return sent, conf, score

def main():
    if not NEWS_FILE.exists():
        print("no news file for today")
        return
    df = pd.read_csv(NEWS_FILE)
    res = []
    for _, r in df.iterrows():
        s, c, raw = analyze_row(r.get("headline",""), r.get("summary",""))
        res.append({
            "time": r["time"],
            "headline": r["headline"],
            "sentiment": s,
            "confidence": c,
            "score": raw
        })
    out = pd.DataFrame(res).sort_values("time", ascending=False)
    out.to_csv(OUT, index=False)
    print(f"saved {len(out)} rows -> {OUT}")

if __name__ == "__main__":
    main()
