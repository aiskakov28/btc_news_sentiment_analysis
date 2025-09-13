from pathlib import Path
import pandas as pd

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def news_path(root: Path, date_str: str) -> Path:
    return root / "news" / f"crypto_news_{date_str}.csv"

def sentiment_path(root: Path, date_str: str) -> Path:
    return root / "sentiment" / f"sentiment_analysis_{date_str}.csv"

def price_path(root: Path, date_str: str) -> Path:
    return root / "prices" / f"bitcoin_prices_{date_str}.csv"

def read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)

def write_csv(df: pd.DataFrame, path: Path) -> Path:
    ensure_dir(path.parent)
    df.to_csv(path, index=False)
    return path
