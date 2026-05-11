# tests/test_returns.py

import pandas as pd
import pytest

from portfolio_builder.analytics.returns import (
    calculate_cumulative_returns,
    calculate_daily_returns,
)


def test_calculate_daily_returns():
    prices = pd.DataFrame(
        {
            "AAPL": [100, 110, 121],
            "MSFT": [200, 220, 242],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
    )

    returns = calculate_daily_returns(prices)

    assert returns.shape == (2, 2)
    assert returns.loc["2024-01-02", "AAPL"] == pytest.approx(0.10)
    assert returns.loc["2024-01-03", "MSFT"] == pytest.approx(0.10)


def test_calculate_cumulative_returns():
    prices = pd.DataFrame(
        {
            "AAPL": [100, 110, 121],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
    )

    cumulative = calculate_cumulative_returns(prices)

    assert cumulative.iloc[-1]["AAPL"] == pytest.approx(0.21)
