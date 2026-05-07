# src/portfolio_builder/data/provider.py

import pandas as pd
import yfinance as yf


def download_adjusted_close(
    tickers: list[str],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    tickers = [ticker.upper().strip() for ticker in tickers]

    data = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        return pd.DataFrame(columns=tickers).rename_axis("date")

    if len(tickers) == 1:
        prices = data[["Adj Close"]].copy()
        prices.columns = tickers
    else:
        prices = data["Adj Close"].copy()

    prices = prices.dropna(how="all")
    prices.index = pd.to_datetime(prices.index)
    prices.index.name = "date"

    return prices
