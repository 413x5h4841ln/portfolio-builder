# src/portfolio_builder/analytics/returns.py

import pandas as pd


def calculate_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()


def calculate_cumulative_returns(prices: pd.DataFrame) -> pd.DataFrame:
    daily_returns = calculate_daily_returns(prices)
    return (1 + daily_returns).cumprod() - 1


def annualized_mean_returns(daily_returns: pd.DataFrame) -> pd.Series:
    return daily_returns.mean() * 252


def annualized_covariance(daily_returns: pd.DataFrame) -> pd.DataFrame:
    return daily_returns.cov() * 252
