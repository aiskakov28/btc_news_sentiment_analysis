import pandas as pd
from datetime import datetime
from pathlib import Path
import types

from src.collectors import news_rss, btc_price

def test_news_rss_parsing(monkeypatch):
    class FakeEntry(dict): pass
    class FakeFeed: entries = [
        FakeEntry(title="BTC surges to record high", link="x", published="Mon, 01 Jan 2024 12:00:00 +0000", summary=""),
        FakeEntry(title="Market crash alert", link="y", published="2024-01-01T13:00:00+0000", summary=""),
    ]
    monkeypatch.setattr(news_rss, "feedparser", types.SimpleNamespace(parse=lambda _u: FakeFeed()))
    rows = news_rss.fetch_feed("coindesk", "u")
    assert len(rows) == 2
    assert rows[0]["source"] == "coindesk"
    assert {"date","time","headline","summary","link"}.issubset(rows[0])

def test_btc_price_storage(tmp_path: Path):
    ts = datetime(2024,1,1,12,0,0)
    fn = btc_price.append_csv(tmp_path, ts, 45000.0)
    assert fn.exists()
    df = btc_price.load_day(tmp_path, "2024-01-01")
    assert isinstance(df, pd.DataFrame)
    assert "datetime" in df.columns
    assert float(df.iloc[0]["price"]) == 45000.0
