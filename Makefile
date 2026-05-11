.PHONY: install test lint format dashboard inspect-cache

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests scripts

format:
	ruff format src tests scripts

dashboard:
	streamlit run src/portfolio_builder/dashboard/app.py

inspect-cache:
	python scripts/inspect_cache.py
