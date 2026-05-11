# Portfolio Builder

A Python application for building, optimizing, and visualizing stock portfolios.

The project combines:

- historical price fetching and local caching
- Markowitz-style portfolio optimization
- efficient frontier calculation
- portfolio performance comparison
- an interactive Streamlit dashboard

## Features

- Fetch historical prices using yfinance
- Cache adjusted close prices in SQLite
- Calculate daily and cumulative returns
- Build equal-weight portfolios
- Optimize max-Sharpe portfolios
- Optimize min-volatility portfolios
- Generate efficient frontiers
- Compare portfolios against individual stocks
- Visualize results in Streamlit

## Project Status

This project is currently in MVP / alpha stage.

Current version: `0.1.0`

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/portfolio-builder.git
cd portfolio-builder

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```
On Windows:

```PowerShell
.venv\Scripts\activate

pip install -e ".[dev]"
```
## Run the CLI

```bash
portfolio-builder
```

## Run the dashboard
```bash
streamlit run src/portfolio_builder/dashboard/app.py
```
## Inspect cached data
```bash
python scripts/inspect_cache.py
```
## Clear cached ticker data
```bash
python scripts/clear_cached_ticker.py AAPL
```
## Run tests
```bash
pytest
```
## Architecture
Dashboard layer:
    Streamlit + Plotly

Analytics layer:
    returns, risk, optimization, performance comparison

Data layer:
    yfinance provider + SQLite cache
