# src/portfolio_builder/analytics/portfolio.py

import numpy as np
import pandas as pd


def equal_weight_portfolio(tickers: list[str]) -> dict[str, float]:
    weight = 1 / len(tickers)
    return {ticker: weight for ticker in tickers}


def portfolio_returns(
    daily_returns: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series:
    weight_vector = np.array([weights[ticker] for ticker in daily_returns.columns])
    return daily_returns @ weight_vector


def portfolio_metrics(
    portfolio_daily_returns: pd.Series,
    risk_free_rate: float = 0.0,
) -> dict[str, float]:
    annual_return = portfolio_daily_returns.mean() * 252
    annual_volatility = portfolio_daily_returns.std() * np.sqrt(252)
    sharpe = (annual_return - risk_free_rate) / annual_volatility

    cumulative = (1 + portfolio_daily_returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1
    max_drawdown = drawdown.min()

    return {
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
    }
