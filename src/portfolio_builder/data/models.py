# src/portfolio_builder/data/models.py

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from portfolio_builder.data.db import Base


class DailyPrice(Base):
    __tablename__ = "daily_prices"

    ticker: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)

    adjusted_close: Mapped[float] = mapped_column(Float, nullable=False)

    source: Mapped[str] = mapped_column(String, nullable=False, default="yfinance")
    inserted_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"DailyPrice("
            f"ticker={self.ticker!r}, "
            f"date={self.date!r}, "
            f"adjusted_close={self.adjusted_close!r})"
        )
