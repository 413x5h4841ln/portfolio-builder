# src/portfolio_builder/data/repository.py

from datetime import date

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import delete

from portfolio_builder.data.models import DailyPrice


def read_prices_from_db(
    session: Session,
    tickers: list[str],
    start_date: str | date,
    end_date: str | date,
) -> pd.DataFrame:
    """
    Read adjusted close prices from the database.

    Returns a wide DataFrame:

        date        AAPL      MSFT
        2020-01-02  72.1      154.2
        2020-01-03  71.8      152.9

    Note:
        end_date is treated as exclusive, matching yfinance behavior.
    """
    start = pd.Timestamp(start_date).date()
    end = pd.Timestamp(end_date).date()

    statement = (
        select(DailyPrice)
        .where(DailyPrice.ticker.in_(tickers))
        .where(DailyPrice.date >= start)
        .where(DailyPrice.date < end)
        .order_by(DailyPrice.date.asc())
    )

    rows = session.execute(statement).scalars().all()

    if not rows:
        return pd.DataFrame(columns=tickers).rename_axis("date")

    records = [
        {
            "date": row.date,
            "ticker": row.ticker,
            "adjusted_close": row.adjusted_close,
        }
        for row in rows
    ]

    df = pd.DataFrame(records)

    prices = df.pivot(
        index="date",
        columns="ticker",
        values="adjusted_close",
    ).sort_index()

    prices.index = pd.to_datetime(prices.index)
    prices.index.name = "date"

    for ticker in tickers:
        if ticker not in prices.columns:
            prices[ticker] = pd.NA

    return prices[tickers]


def upsert_prices_to_db(
    session: Session,
    prices: pd.DataFrame,
    source: str = "yfinance",
) -> None:
    """
    Insert or update adjusted close prices.

    Expects a wide DataFrame:

        date        AAPL      MSFT
        2020-01-02  72.1      154.2
    """
    if prices.empty:
        return

    records = []

    for timestamp, row in prices.iterrows():
        price_date = pd.Timestamp(timestamp).date()

        for ticker, adjusted_close in row.dropna().items():
            records.append(
                {
                    "ticker": str(ticker).upper(),
                    "date": price_date,
                    "adjusted_close": float(adjusted_close),
                    "source": source,
                }
            )

    if not records:
        return

    statement = insert(DailyPrice).values(records)

    update_statement = statement.on_conflict_do_update(
        index_elements=["ticker", "date"],
        set_={
            "adjusted_close": statement.excluded.adjusted_close,
            "source": statement.excluded.source,
        },
    )

    session.execute(update_statement)
    session.commit()

def list_cached_tickers(session: Session) -> pd.DataFrame:
    """
    Return one row per cached ticker.

    Columns:
        ticker
        start_date
        end_date
        rows
    """
    statement = (
        select(
            DailyPrice.ticker,
            func.min(DailyPrice.date).label("start_date"),
            func.max(DailyPrice.date).label("end_date"),
            func.count(DailyPrice.date).label("rows"),
        )
        .group_by(DailyPrice.ticker)
        .order_by(DailyPrice.ticker)
    )

    rows = session.execute(statement).all()

    if not rows:
        return pd.DataFrame(
            columns=["ticker", "start_date", "end_date", "rows"]
        )

    return pd.DataFrame(
        rows,
        columns=["ticker", "start_date", "end_date", "rows"],
    )

def delete_ticker_prices(
    session: Session,
    ticker: str,
) -> int:
    """
    Delete all cached prices for one ticker.

    Returns the number of deleted rows.
    """
    ticker = ticker.upper().strip()

    statement = delete(DailyPrice).where(DailyPrice.ticker == ticker)

    result = session.execute(statement)
    session.commit()

    return result.rowcount or 0
