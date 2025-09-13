# 🧠📈 BTC News Sentiment Analysis

Turn crypto headlines into **actionable sentiment signals**; then visualize them alongside price in a clean **Streamlit** app.

<p align="left">
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white"></a>
  <a href="#"><img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white"></a>
  <a href="#"><img alt="Transformers" src="https://img.shields.io/badge/Transformers-RoBERTa-FFD21E?logo=huggingface&logoColor=000"></a>
  <a href="#"><img alt="License" src="https://img.shields.io/badge/License-MIT-2ea44f"></a>
</p>

> **Disclaimer:** This project is for **educational purposes only** and **not financial advice**.

---

## 🔎 What You Get

- **Multi-source news ingestion** (14+ crypto RSS feeds)
- **Ensemble sentiment**: *VADER* + *TextBlob* + *Hugging Face (RoBERTa)* + *market lexicon*
- **Time-window features**: momentum, ratio, strength, volume
- **Direction forecast**: `UP / DOWN / NEUTRAL` + confidence (≤ 95%)
- **Streamlit dashboard**: price overlays, rolling sentiment, latest headlines
- **CLI pipeline** + **Docker** + **pytest** suite

---

## 🗺️ Table of Contents

- [Architecture](#-architecture)
- [Project Layout](#-project-layout)
- [Quickstart](#-quickstart)
- [Pipeline (CLI)](#-pipeline-cli)
- [Configuration](#-configuration)
- [Data Artifacts](#-data-artifacts)
- [Testing](#-testing)
- [Docker](#-docker)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🧩 Architecture

```text
RSS Feeds ─┐
           ├─► Collectors (feedparser) ─► cleaned CSV
Price API ─┘
                           │
                           ▼
              Sentiment Ensemble
     (VADER + TextBlob + RoBERTa + Lexicon)
                           │
                           ▼
           Time-Window Features (rolling, ratios)
                           │
                           ▼
        Forecast Rules (direction + confidence)
                           │
                           ▼
             Streamlit UI (charts + table)
```

### 📦 Project Layout

```text
app/                 # Streamlit UI
config/              # YAML configs: app/data/model
data/{news,prices,sentiment}/
scripts/             # CLI: collect → analyze → forecast → backfill
src/
  collectors/        # rss_sources, news_rss, btc_price
  processing/        # clean
  sentiment/         # vader, transformers, indicators, ensemble
  features/          # time_windows
  forecasting/       # rules
  io/                # storage
  utils/             # clock, logging
tests/               # pytest
```

### 🚀 Quickstart

```bash
# 1) Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2) Run Streamlit app
make app
# http://localhost:8501
```
Tip: edit config/model.yaml to tweak weights/thresholds and config/data.yaml to adjust sources & retention.

### 🔗 Pipeline (CLI)

```bash
# 1) Collect latest headlines into data/news/crypto_news_YYYY-MM-DD.csv
make collect

# 2) Analyze sentiment into data/sentiment/sentiment_analysis_YYYY-MM-DD.csv
make analyze

# 3) Print a one-line forecast like: "UP 0.72"
make forecast
```
Backfill a past date:

```bash
DATE=2024-01-01 make backfill
```

### ⚙️ Configuration

```yaml
| File                | Purpose        | Key Fields                                        |
| ------------------- | -------------- | ------------------------------------------------- |
| config/app.yaml   | UI & paths     | title, paths.data_root                        |
| config/data.yaml  | ingestion      | sources, interval_minutes, retention_days   |
| config/model.yaml | models & rules | hf_model, weights, thresholds, prediction |

```
Minimal environment:

```bash
LOCAL_TZ=UTC
HF_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest
```

### 📦 Data Artifacts

```text
| Path                                               | Description                                |
| -------------------------------------------------- | ------------------------------------------ |
| data/news/crypto_news_YYYY-MM-DD.csv             | date,time,headline,source,link,summary   |
| data/sentiment/sentiment_analysis_YYYY-MM-DD.csv | time,headline,sentiment,confidence,score |
| data/prices/bitcoin_prices_YYYY-MM-DD.csv        | date,time,price                          |
```

### ✅ Testing
```bash
make test   # runs pytest across collectors, processing, sentiment, features, forecasting
```

### 🐳 Docker
```bash
docker build -t btc-sentiment .
docker run -p 8501:8501 --env-file .env btc-sentiment
# open http://localhost:8501
```

### 🗺️ Roadmap
* **Price overlay auto-fetch & caching**
* **Lightweight ML calibration for ensemble weights**
* **More sources + tweet stream option** 
* **REST endpoint for real-time forecasts**

### 📝 License
**MIT License**