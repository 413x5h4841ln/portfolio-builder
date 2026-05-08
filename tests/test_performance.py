import numpy as np
import pandas as pd
import pytest

from portfolio_builder.analytics.performance import (
    compare_metrics,
    compare_return_series,
    cumulative_returns,
    drawdown_series,
    performance_metrics,
    portfolio_daily_returns,
)


def test_portfolio_daily_returns_equal_weight():
    daily_returns = pd.DataFrame(
        {
            "AAPL": [0.01, 0.02, -0.01],
            "MSFT": [0.03, -0.01, 0.02],
        }
    )

    weights = {
        "AAPL": 0.5,
        "MSFT": 0.5,
    }

    result = portfolio_daily_returns(daily_returns, weights)

    expected = pd.Series([0.02, 0.005, 0.005], name="portfolio_return")

    pd.testing.assert_series_equal(result.reset_index(drop=True), expected)


def test_portfolio_daily_returns_rejects_bad_weight_sum():
    daily_returns = pd.DataFrame(
        {
            "AAPL": [0.01, 0.02],
            "MSFT": [0.03, -0.01],
        }
    )

    weights = {
        "AAPL": 0.5,
        "MSFT": 0.4,
    }

    with pytest.raises(ValueError):
        portfolio_daily_returns(daily_returns, weights)


def test_cumulative_returns():
    daily_returns = pd.Series([0.10, -0.10])

    result = cumulative_returns(daily_returns)

    assert np.isclose(result.iloc[-1], -0.01)


def test_drawdown_series():
    daily_returns = pd.Series([0.10, -0.20, 0.05])

    result = drawdown_series(daily_returns)

    assert result.min() < 0


def test_performance_metrics_contains_expected_keys():
    daily_returns = pd.Series([0.01, -0.005, 0.002, 0.004])

    metrics = performance_metrics(daily_returns)

    assert "total_return" in metrics
    assert "annual_return" in metrics
    assert "annual_volatility" in metrics
    assert "sharpe_ratio" in metrics
    assert "max_drawdown" in metrics


def test_compare_return_series():
    daily_returns = pd.DataFrame(
        {
            "AAPL": [0.01, 0.02],
            "MSFT": [0.03, -0.01],
        }
    )

    portfolios = {
        "Equal Weight": {
            "AAPL": 0.5,
            "MSFT": 0.5,
        }
    }

    result = compare_return_series(daily_returns, portfolios)

    assert "Equal Weight" in result.columns
    assert len(result) == 2


def test_compare_metrics():
    returns = pd.DataFrame(
        {
            "Portfolio A": [0.01, 0.02, -0.01],
            "Portfolio B": [0.005, 0.005, 0.005],
        }
    )

    result = compare_metrics(returns)

    assert "Portfolio A" in result.index
    assert "Portfolio B" in result.index
