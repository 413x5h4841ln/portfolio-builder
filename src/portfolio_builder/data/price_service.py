# src/portfolio_builder/data/price_service.py

from datetime import date

import pandas as pd

from portfolio_builder.data.db import SessionLocal, init_db
from portfolio_builder.data.provider import download_adjusted_close
from portfolio_builder.data.repository import (
    read_prices_from_db,
    upsert_prices_to_db,
)


def _normalize_tickers(tickers: list[str]) -> list[str]:
    return sorted({ticker.upper().strip() for ticker in tickers if ticker.strip()})


def _get_missing_edge_ranges(
    cached_prices: pd.DataFrame,
    ticker: str,
    start_date: str | date,
    end_date: str | date,
) -> list[tuple[str, str]]:
    """
    Return missing ranges at the beginning or end of the requested period.

    This MVP intentionally handles missing edge ranges.
    Later, we can add detection for holes inside the date range.
    """
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    if ticker not in cached_prices.columns:
        return [(start.date().isoformat(), end.date().isoformat())]

    series = cached_prices[ticker].dropna()

    if series.empty:
        return [(start.date().isoformat(), end.date().isoformat())]

    first_cached_date = pd.Timestamp(series.index.min())
    last_cached_date = pd.Timestamp(series.index.max())

    expected_business_days = pd.bdate_range(
        start=start,
        end=end - pd.Timedelta(days=1),
    )

    if expected_business_days.empty:
        return []

    first_expected_date = expected_business_days[0]
    last_expected_date = expected_business_days[-1]

    missing_ranges = []

    if first_cached_date > first_expected_date:
        missing_ranges.append(
            (
                start.date().isoformat(),
                first_cached_date.date().isoformat(),
            )
        )

    if last_cached_date < last_expected_date:
        download_start = last_cached_date + pd.Timedelta(days=1)

        missing_ranges.append(
            (
                download_start.date().isoformat(),
                end.date().isoformat(),
            )
        )

    return missing_ranges


def get_price_history(
    tickers: list[str],
    start_date: str | date,
    end_date: str | date,
) -> pd.DataFrame:
    """
    Get adjusted close prices.

    Process:
    1. Initialize database.
    2. Read whatever exists locally.
    3. Download missing ranges from yfinance.
    4. Save downloaded data.
    5. Read final result from the database.

    end_date is exclusive, matching yfinance behavior.
    """
    tickers = _normalize_tickers(tickers)

    if not tickers:
        raise ValueError("At least one ticker is required.")

    if pd.Timestamp(start_date) >= pd.Timestamp(end_date):
        raise ValueError("start_date must be before end_date.")

    init_db()

    with SessionLocal() as session:
        cached_prices = read_prices_from_db(
            session=session,
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
        )

        for ticker in tickers:
            missing_ranges = _get_missing_edge_ranges(
                cached_prices=cached_prices,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
            )

            for missing_start, missing_end in missing_ranges:
                downloaded_prices = download_adjusted_close(
                    tickers=[ticker],
                    start_date=missing_start,
                    end_date=missing_end,
                )

                upsert_prices_to_db(
                    session=session,
                    prices=downloaded_prices,
                    source="yfinance",
                )

        final_prices = read_prices_from_db(
            session=session,
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
        )

    return final_prices.dropna(how="all")
