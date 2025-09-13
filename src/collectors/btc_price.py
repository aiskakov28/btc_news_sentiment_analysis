from datetime import datetime
from pathlib import Path
import csv, requests, pandas as pd

TZ = datetime.now().astimezone().tzinfo

def get_price_point(ts: datetime) -> dict | None:
    r = requests.get("https://api.coinlore.net/api/ticker/?id=90", timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()[0]
    return {"timestamp": ts, "price": float(data["price_usd"])}

def append_csv(root: Path, ts: datetime, price: float) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    fn = root / f"bitcoin_prices_{ts.strftime('%Y-%m-%d')}.csv"
    header = ["date","time","price"]
    mode = "a" if fn.exists() else "w"
    with open(fn, mode, newline="") as f:
        w = csv.writer(f)
        if mode == "w":
            w.writerow(header)
        w.writerow([ts.strftime("%Y-%m-%d"), ts.strftime("%H:%M:%S"), price])
    return fn

def load_day(root: Path, day: str) -> pd.DataFrame | None:
    fn = root / f"bitcoin_prices_{day}.csv"
    if not fn.exists():
        return None
    df = pd.read_csv(fn)
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
    return df.sort_values("datetime")
