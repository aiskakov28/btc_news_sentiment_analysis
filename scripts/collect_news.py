from pathlib import Path
from datetime import datetime
import time, csv, glob, yaml, feedparser, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "data.yaml"
DATA = ROOT / "data" / "news"
DATA.mkdir(parents=True, exist_ok=True)

def yml(p):
    with open(p) as f:
        return yaml.safe_load(f)

cfg = yml(CFG)
TZ = datetime.now().astimezone().tzinfo
DATE = datetime.now(TZ).strftime("%Y-%m-%d")
OUT = DATA / f"crypto_news_{DATE}.csv"

def parse_date(s):
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z").astimezone(TZ)
    except:
        try:
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z").astimezone(TZ)
        except:
            return datetime.now(TZ)

def fetch_source(name, url):
    feed = feedparser.parse(url)
    rows = []
    for e in feed.entries:
        dt = parse_date(e.get("published", ""))
        rows.append({
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "headline": e.get("title", "").strip(),
            "source": name,
            "link": e.get("link", ""),
            "summary": (e.get("summary","") or "").strip()[:240]
        })
    return rows

def load_existing(path):
    if not path.exists():
        return set()
    try:
        df = pd.read_csv(path)
        return set(df["headline"])
    except:
        return set()

def write_csv(path, rows):
    header = ["date","time","headline","source","link","summary"]
    if path.exists():
        df_old = pd.read_csv(path).to_dict("records")
    else:
        df_old = []
    all_rows = rows + df_old
    all_rows.sort(key=lambda r: r["time"], reverse=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows(all_rows)

def main():
    seen = load_existing(OUT)
    new_rows = []
    for name, url in cfg["sources"].items():
        new_rows += [r for r in fetch_source(name, url) if r["date"] == DATE and r["headline"] not in seen]
        time.sleep(0.5)
    if new_rows:
        write_csv(OUT, new_rows)
    print(f"wrote {len(new_rows)} new rows -> {OUT}")

if __name__ == "__main__":
    main()
