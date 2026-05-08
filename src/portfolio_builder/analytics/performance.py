# src/portfolio_builder/analytics/performance.py

import numpy as np
import pandas as pd


def align_weights(
    weights: dict[str, float],
    tickers: list[str],
) -> np.ndarray:
    """
    Convert a weights dictionary into a NumPy array aligned to ticker order.

    Missing tickers get weight 0.
    """
    return np.array([weights.get(ticker, 0.0) for ticker in tickers])


def portfolio_daily_returns(
    daily_returns: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series:
    """
    Calculate portfolio daily returns from asset returns and weights.
    """
    tickers = list(daily_returns.columns)
    weight_vector = align_weights(weights, tickers)

    if not np.isclose(weight_vector.sum(), 1.0):
        raise ValueError(
            f"Portfolio weights must sum to 1. Current sum: {weight_vector.sum():.6f}"
        )

    returns = daily_returns @ weight_vector
    returns.name = "portfolio_return"

    return returns


def cumulative_returns(daily_returns: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    """
    Convert daily returns into cumulative returns.
    """
    return (1 + daily_returns).cumprod() - 1


def drawdown_series(daily_returns: pd.Series) -> pd.Series:
    """
    Calculate drawdown series from daily returns.
    """
    wealth = (1 + daily_returns).cumprod()
    running_max = wealth.cummax()
    drawdown = wealth / running_max - 1

    return drawdown


def performance_metrics(
    daily_returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252,
) -> dict[str, float]:
    """
    Calculate common performance metrics from daily returns.
    """
    if daily_returns.empty:
        raise ValueError("daily_returns cannot be empty.")

    annual_return = daily_returns.mean() * periods_per_year
    annual_volatility = daily_returns.std() * np.sqrt(periods_per_year)

    if annual_volatility == 0:
        sharpe_ratio = np.nan
    else:
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility

    cumulative = cumulative_returns(daily_returns)
    total_return = cumulative.iloc[-1]

    max_drawdown = drawdown_series(daily_returns).min()

    return {
        "total_return": float(total_return),
        "annual_return": float(annual_return),
        "annual_volatility": float(annual_volatility),
        "sharpe_ratio": float(sharpe_ratio),
        "max_drawdown": float(max_drawdown),
    }


def compare_return_series(
    daily_returns: pd.DataFrame,
    portfolios: dict[str, dict[str, float]],
) -> pd.DataFrame:
    """
    Build a DataFrame of daily returns for multiple portfolios.

    Args:
        daily_returns:
            Asset daily returns.
        portfolios:
            Example:
                {
                    "Equal Weight": {"AAPL": 0.33, "MSFT": 0.33, "NVDA": 0.34},
                    "Max Sharpe": {"AAPL": 0.10, "MSFT": 0.20, "NVDA": 0.70},
                }

    Returns:
        DataFrame where columns are portfolio names.
    """
    result = pd.DataFrame(index=daily_returns.index)

    for name, weights in portfolios.items():
        result[name] = portfolio_daily_returns(daily_returns, weights)

    return result


def compare_metrics(
    return_series: pd.DataFrame,
    risk_free_rate: float = 0.02,
) -> pd.DataFrame:
    """
    Calculate metrics for each column in a returns DataFrame.
    """
    rows = []

    for name in return_series.columns:
        metrics = performance_metrics(
            return_series[name].dropna(),
            risk_free_rate=risk_free_rate,
        )
        metrics["name"] = name
        rows.append(metrics)

    metrics_df = pd.DataFrame(rows).set_index("name")

    return metrics_df[
        [
            "total_return",
            "annual_return",
            "annual_volatility",
            "sharpe_ratio",
            "max_drawdown",
        ]
    ]


def normalized_price_performance(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Convert price history into normalized cumulative performance.

    Each asset starts at 0%.
    """
    return prices / prices.iloc[0] - 1
