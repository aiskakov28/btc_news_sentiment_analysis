from datetime import datetime
from typing import List, Dict
import feedparser

TZ = datetime.now().astimezone().tzinfo

def _parse_date(s: str) -> datetime:
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s, fmt).astimezone(TZ)
        except Exception:
            continue
    return datetime.now(TZ)

def fetch_feed(name: str, url: str) -> List[Dict]:
    feed = feedparser.parse(url)
    rows = []
    for e in feed.entries:
        dt = _parse_date(e.get("published", ""))
        rows.append({
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "headline": e.get("title", "").strip(),
            "source": name,
            "link": e.get("link", ""),
            "summary": (e.get("summary","") or "").strip()[:240],
        })
    return rows
