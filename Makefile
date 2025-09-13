.PHONY: setup app collect analyze forecast backfill test

setup:
	pip install -r requirements.txt
	python -m textblob.download_corpora

app:
	streamlit run app/streamlit_app.py

collect:
	python scripts/collect_news.py

analyze:
	python scripts/analyze_sentiment.py

forecast:
	python scripts/forecast_direction.py

backfill:
	python scripts/backfill_day.py $(DATE)

test:
	pytest -q
