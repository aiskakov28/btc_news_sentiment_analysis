import os
import csv
import json
import feedparser
from datetime import datetime, timezone, timedelta
import time
import logging
import sys
from pathlib import Path
import pandas as pd
import pytz

# Get local timezone
local_tz = datetime.now().astimezone().tzinfo

# Get project root and configure paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_DIR / 'crypto_news_collector.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CryptoNewsCollector:
    def __init__(self, interval_minutes=5):
        self.interval_seconds = interval_minutes * 60
        self.output_dir = DATA_DIR / "news"
        self.output_dir.mkdir(exist_ok=True)
        self.sources = {
            'coindesk': "https://www.coindesk.com/arc/outboundfeeds/rss/",
            'cointelegraph': "https://cointelegraph.com/rss",
            'cryptonews': "https://cryptonews.com/news/feed",
            'decrypt': "https://decrypt.co/feed",
            'beincrypto': "https://beincrypto.com/feed/",
            'bitcoinist': "https://bitcoinist.com/feed/",
            'cryptoslate': "https://cryptoslate.com/feed/",
            'newsbtc': "https://www.newsbtc.com/feed/",
            'ambcrypto': "https://ambcrypto.com/feed/",
            'cryptopotato': "https://cryptopotato.com/feed/",
            'theblock': "https://www.theblock.co/rss.xml",
            'cryptobriefing': "https://cryptobriefing.com/feed/",
            'dailyhodl': "https://dailyhodl.com/feed/",
            'bitcoincom': "https://news.bitcoin.com/feed/"
        }

    def parse_date(self, date_str):
        try:
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            return dt.astimezone(local_tz)
        except:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                return dt.astimezone(local_tz)
            except:
                return datetime.now(local_tz)

    def get_news_from_source(self, source_name, source_url):
        try:
            feed = feedparser.parse(source_url)
            news_items = []
            for entry in feed.entries:
                pub_date = self.parse_date(entry.get('published', '')) if 'published' in entry else datetime.now(local_tz)
                news_items.append({
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "time": pub_date.strftime("%H:%M:%S"),
                    "headline": entry.title,
                    "source": source_name,
                    "link": entry.link,
                    "summary": entry.get('summary', '').strip()[:200] + '...' if 'summary' in entry else ''
                })
            return news_items
        except Exception as e:
            logging.error(f"Error fetching {source_name} news: {e}")
            return []

    def get_all_news(self):
        all_news = []
        seen_headlines = set()
        current_date = datetime.now(local_tz).strftime("%Y-%m-%d")

        # First load existing headlines from today's file
        filename = self.output_dir / f"crypto_news_{current_date}.csv"
        if filename.exists():
            try:
                df = pd.read_csv(filename)
                seen_headlines.update(set(df['headline']))
            except Exception as e:
                logging.error(f"Error reading existing CSV: {e}")

        for source_name, source_url in self.sources.items():
            news_items = self.get_news_from_source(source_name, source_url)
            for item in news_items:
                if item['date'] == current_date and item['headline'] not in seen_headlines:
                    seen_headlines.add(item['headline'])
                    all_news.append(item)
            time.sleep(1)

        return sorted(all_news, key=lambda x: x['time'], reverse=True)

    def append_to_csv(self, data):
        if not data:
            return

        current_date = datetime.now(local_tz).strftime("%Y-%m-%d")
        filename = self.output_dir / f"crypto_news_{current_date}.csv"

        try:
            existing_data = []
            if filename.exists():
                # Read existing data
                existing_data = pd.read_csv(filename).to_dict('records')

            # Combine new and existing data
            all_data = data + existing_data

            # Sort all data by time in descending order
            sorted_data = sorted(all_data, key=lambda x: x['time'], reverse=True)

            # Write all data to file
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile,
                                      fieldnames=["date", "time", "headline", "source", "link", "summary"])
                writer.writeheader()
                writer.writerows(sorted_data)

            logging.info(f"Added {len(data)} new articles to {filename}")
        except Exception as e:
            logging.error(f"Error writing to CSV: {e}")

    def create_daily_summary(self, data):
        current_date = datetime.now(local_tz).strftime("%Y-%m-%d")
        summary_file = self.output_dir / f"summary_{current_date}.txt"

        try:
            # Read existing news first
            existing_news = []
            filename = self.output_dir / f"crypto_news_{current_date}.csv"
            if filename.exists():
                df = pd.read_csv(filename)
                existing_news = df.to_dict('records')

            # Combine with new news and sort by time
            all_news = sorted(existing_news + data, key=lambda x: x['time'], reverse=True)

            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"Crypto News Summary for {current_date}\n")
                f.write("=" * 50 + "\n\n")

                news_by_source = {}
                for item in all_news:
                    if item['source'] not in news_by_source:
                        news_by_source[item['source']] = []
                    news_by_source[item['source']].append(item)

                for source, items in news_by_source.items():
                    f.write(f"\n{source} News:\n")
                    f.write("-" * 30 + "\n")
                    for item in sorted(items, key=lambda x: x['time'], reverse=True):
                        f.write(f"[{item['time']}] {item['headline']}\n")
                    f.write("\n")

            logging.info(f"Daily summary created: {summary_file}")
        except Exception as e:
            logging.error(f"Error creating daily summary: {e}")

    def cleanup_old_files(self, days_to_keep=30):
        current_time = datetime.now(local_tz)
        for file in self.output_dir.glob("*"):
            if file.is_file():
                file_time = datetime.fromtimestamp(file.stat().st_mtime)
                if (current_time - file_time).days > days_to_keep:
                    file.unlink()
                    logging.info(f"Deleted old file: {file}")

    def run(self):
        logging.info("Starting Crypto News collection")
        print(f"Collecting news from {len(self.sources)} sources")
        print(f"Using timezone: {local_tz}")
        print(f"Data will be saved to: {self.output_dir}")

        try:
            while True:
                news_data = self.get_all_news()
                if news_data:
                    self.append_to_csv(news_data)
                    self.create_daily_summary(news_data)
                    print(f"Data collected at {datetime.now(local_tz)}: {len(news_data)} articles")

                if datetime.now(local_tz).hour == 0 and datetime.now(local_tz).minute < 1:
                    self.cleanup_old_files()

                time.sleep(self.interval_seconds)
        except KeyboardInterrupt:
            logging.info("News collection stopped by user")
            sys.exit(0)

if __name__ == "__main__":
    collector = CryptoNewsCollector(interval_minutes=5)
    collector.run()