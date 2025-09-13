import os
from pathlib import Path
from datetime import datetime
import glob
import yaml
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config"

def load_yaml(p):
    with open(p, "r") as f:
        return yaml.safe_load(f)

app_cfg = load_yaml(CFG / "app.yaml")
data_cfg = load_yaml(CFG / "data.yaml")
model_cfg = load_yaml(CFG / "model.yaml")

DATA_DIR = ROOT / app_cfg["paths"]["data_root"]
NEWS_DIR = DATA_DIR / "news"
SENT_DIR = DATA_DIR / "sentiment"
PRICE_DIR = DATA_DIR / "prices"

st.set_page_config(page_title=app_cfg["title"], layout="wide")
st.title(app_cfg["title"])
st.caption(app_cfg["subtitle"])

col1, col2, col3 = st.columns(3)
with col1:
    lookback = st.slider("Lookback (minutes)", 15, 240, model_cfg["prediction"]["lookback_minutes"], step=15)
with col2:
    resample = st.selectbox("Resample", ["5min","15min","30min","60min"], index=2)
with col3:
    date_str = st.date_input("Date", datetime.now()).strftime("%Y-%m-%d")

def load_latest_sentiment(date_str: str) -> pd.DataFrame | None:
    patt = str(SENT_DIR / f"sentiment_analysis_{date_str}.csv")
    files = glob.glob(patt)
    if not files:
        return None
    df = pd.read_csv(files[0])
    if "time" in df.columns:
        df["datetime"] = pd.to_datetime(date_str + " " + df["time"])
    elif "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
    else:
        return None
    df = df.sort_values("datetime")
    if {"sentiment","confidence"}.issubset(df.columns):
        df["weighted_sentiment"] = df["sentiment"] * df["confidence"]
    return df

def load_latest_price(date_str: str) -> pd.DataFrame | None:
    patt_new = str(PRICE_DIR / f"bitcoin_prices_{date_str}.csv")
    patt_legacy = str(DATA_DIR / f"bitcoin_data_{date_str}.csv")
    cand = glob.glob(patt_new) or glob.glob(patt_legacy)
    if not cand:
        return None
    df = pd.read_csv(cand[0])
    if {"date","time","price_usd"}.issubset(df.columns):
        df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
        df.rename(columns={"price_usd":"price"}, inplace=True)
    elif {"datetime","price"}.issubset(df.columns):
        df["datetime"] = pd.to_datetime(df["datetime"])
    else:
        return None
    return df.sort_values("datetime")

def make_series(df: pd.DataFrame, value_col: str, rule: str) -> pd.DataFrame:
    ts = (
        df.set_index("datetime")[[value_col]]
          .resample(rule).mean()
          .dropna()
          .reset_index()
    )
    ts.rename(columns={value_col: value_col}, inplace=True)
    return ts

sent_df = load_latest_sentiment(date_str)
price_df = load_latest_price(date_str)

left, right = st.columns([2,1])

with left:
    if price_df is not None:
        price_ts = make_series(price_df, "price", resample)
        fig_price = px.line(price_ts, x="datetime", y="price", title="BTC Price")
        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("No price data for selected date.")

    if sent_df is not None:
        sent_ts = make_series(sent_df, "weighted_sentiment", resample)
        sent_ts["rolling"] = sent_ts["weighted_sentiment"].rolling(max(1, lookback // 5)).mean()
        fig_sent = px.line(sent_ts, x="datetime", y=["weighted_sentiment","rolling"], title="Weighted Sentiment")
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.info("No sentiment data for selected date.")

with right:
    st.subheader("Snapshot")
    if sent_df is not None:
        recent_cut = sent_df["datetime"].max() - pd.Timedelta(minutes=lookback)
        recent = sent_df[sent_df["datetime"] >= recent_cut]
        daily = sent_df
        r_avg = (recent["sentiment"] * recent["confidence"]).mean() if not recent.empty else 0.0
        d_avg = (daily["sentiment"] * daily["confidence"]).mean() if not daily.empty else 0.0
        momentum = r_avg - d_avg
        ratio = 0.0
        if not recent.empty and "weighted_sentiment" in recent:
            cls = recent["weighted_sentiment"].apply(lambda x: 1 if x > model_cfg["thresholds"]["sentiment"] else (-1 if x < -model_cfg["thresholds"]["sentiment"] else 0))
            pos = (cls == 1).sum()
            neg = (cls == -1).sum()
            if pos + neg > 0:
                ratio = (pos - neg) / (pos + neg)

        if len(recent) < model_cfg["prediction"]["min_articles"]:
            direction = "NEUTRAL"
        elif abs(momentum) < model_cfg["thresholds"]["momentum"]:
            direction = "UP" if ratio > 0.3 else ("DOWN" if ratio < -0.3 else "NEUTRAL")
        else:
            direction = "UP" if momentum > 0 else "DOWN"

        st.metric("Direction (next hour)", direction)
        st.write(f"Recent avg: **{r_avg:.3f}**")
        st.write(f"Daily avg: **{d_avg:.3f}**")
        st.write(f"Momentum: **{momentum:.3f}**")
        st.write(f"Pos/Neg ratio: **{ratio:.2f}**")
    else:
        st.write("—")

st.divider()
st.subheader("Latest Articles")
if sent_df is not None:
    cols = ["time","headline","sentiment","confidence"]
    display_cols = [c for c in cols if c in sent_df.columns]
    st.dataframe(sent_df[display_cols].sort_values("time", ascending=False).head(50), use_container_width=True, height=420)
else:
    st.write("—")
