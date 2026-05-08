import pandas as pd

from portfolio_builder.analytics.optimizer import (
    max_sharpe_portfolio,
    min_volatility_portfolio,
)


def test_max_sharpe_weights_sum_to_one():
    mean_returns = pd.Series(
        {
            "AAPL": 0.20,
            "MSFT": 0.15,
            "NVDA": 0.30,
        }
    )

    cov_matrix = pd.DataFrame(
        [
            [0.10, 0.02, 0.03],
            [0.02, 0.08, 0.02],
            [0.03, 0.02, 0.15],
        ],
        index=["AAPL", "MSFT", "NVDA"],
        columns=["AAPL", "MSFT", "NVDA"],
    )

    portfolio = max_sharpe_portfolio(
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=0.02,
    )

    assert abs(sum(portfolio.weights.values()) - 1) < 1e-5


def test_min_volatility_weights_sum_to_one():
    mean_returns = pd.Series(
        {
            "AAPL": 0.20,
            "MSFT": 0.15,
            "NVDA": 0.30,
        }
    )

    cov_matrix = pd.DataFrame(
        [
            [0.10, 0.02, 0.03],
            [0.02, 0.08, 0.02],
            [0.03, 0.02, 0.15],
        ],
        index=["AAPL", "MSFT", "NVDA"],
        columns=["AAPL", "MSFT", "NVDA"],
    )

    portfolio = min_volatility_portfolio(
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=0.02,
    )

    assert abs(sum(portfolio.weights.values()) - 1) < 1e-5
