# src/portfolio_builder/analytics/optimizer.py

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass
class OptimizedPortfolio:
    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float


def portfolio_performance(
    weights: np.ndarray,
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.0,
) -> tuple[float, float, float]:
    """
    Calculate annualized portfolio return, volatility, and Sharpe ratio.
    """
    expected_return = float(weights @ mean_returns.values)
    volatility = float(np.sqrt(weights.T @ cov_matrix.values @ weights))

    if volatility == 0:
        sharpe_ratio = np.nan
    else:
        sharpe_ratio = (expected_return - risk_free_rate) / volatility

    return expected_return, volatility, sharpe_ratio


def _validate_inputs(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
) -> None:
    if mean_returns.empty:
        raise ValueError("mean_returns cannot be empty.")

    if cov_matrix.empty:
        raise ValueError("cov_matrix cannot be empty.")

    if list(mean_returns.index) != list(cov_matrix.index):
        raise ValueError("mean_returns index must match cov_matrix index.")

    if list(cov_matrix.index) != list(cov_matrix.columns):
        raise ValueError("cov_matrix index must match cov_matrix columns.")


def _make_result(
    weights: np.ndarray,
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float,
) -> OptimizedPortfolio:
    expected_return, volatility, sharpe_ratio = portfolio_performance(
        weights=weights,
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
    )

    cleaned_weights = {
        ticker: float(round(weight, 6))
        for ticker, weight in zip(mean_returns.index, weights)
        if abs(weight) > 1e-6
    }

    return OptimizedPortfolio(
        weights=cleaned_weights,
        expected_return=expected_return,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio,
    )


def max_sharpe_portfolio(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.02,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> OptimizedPortfolio:
    """
    Find the long-only portfolio with the highest Sharpe ratio.

    Args:
        mean_returns:
            Annualized expected returns.
        cov_matrix:
            Annualized covariance matrix.
        risk_free_rate:
            Annualized risk-free rate.
        min_weight:
            Minimum allowed weight per asset.
        max_weight:
            Maximum allowed weight per asset.

    Returns:
        OptimizedPortfolio
    """
    _validate_inputs(mean_returns, cov_matrix)

    n_assets = len(mean_returns)
    initial_weights = np.repeat(1 / n_assets, n_assets)

    bounds = tuple((min_weight, max_weight) for _ in range(n_assets))

    constraints = (
        {
            "type": "eq",
            "fun": lambda weights: np.sum(weights) - 1,
        },
    )

    def objective(weights: np.ndarray) -> float:
        _, _, sharpe_ratio = portfolio_performance(
            weights=weights,
            mean_returns=mean_returns,
            cov_matrix=cov_matrix,
            risk_free_rate=risk_free_rate,
        )

        return -sharpe_ratio

    result = minimize(
        objective,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    if not result.success:
        raise ValueError(f"Optimization failed: {result.message}")

    return _make_result(
        weights=result.x,
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
    )


def min_volatility_portfolio(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.02,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> OptimizedPortfolio:
    """
    Find the long-only portfolio with the lowest volatility.
    """
    _validate_inputs(mean_returns, cov_matrix)

    n_assets = len(mean_returns)
    initial_weights = np.repeat(1 / n_assets, n_assets)

    bounds = tuple((min_weight, max_weight) for _ in range(n_assets))

    constraints = (
        {
            "type": "eq",
            "fun": lambda weights: np.sum(weights) - 1,
        },
    )

    def objective(weights: np.ndarray) -> float:
        volatility = np.sqrt(weights.T @ cov_matrix.values @ weights)
        return float(volatility)

    result = minimize(
        objective,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    if not result.success:
        raise ValueError(f"Optimization failed: {result.message}")

    return _make_result(
        weights=result.x,
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
    )


def efficient_frontier(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.02,
    points: int = 50,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> pd.DataFrame:
    """
    Calculate points on the efficient frontier.

    Returns a DataFrame with:
        expected_return
        volatility
        sharpe_ratio
        one weight column per ticker
    """
    _validate_inputs(mean_returns, cov_matrix)

    n_assets = len(mean_returns)
    initial_weights = np.repeat(1 / n_assets, n_assets)
    bounds = tuple((min_weight, max_weight) for _ in range(n_assets))

    min_target = float(mean_returns.min())
    max_target = float(mean_returns.max())

    target_returns = np.linspace(min_target, max_target, points)

    frontier_rows = []

    for target_return in target_returns:
        constraints = (
            {
                "type": "eq",
                "fun": lambda weights: np.sum(weights) - 1,
            },
            {
                "type": "eq",
                "fun": lambda weights, target=target_return: (
                    weights @ mean_returns.values
                )
                - target,
            },
        )

        def objective(weights: np.ndarray) -> float:
            variance = weights.T @ cov_matrix.values @ weights
            return float(variance)

        result = minimize(
            objective,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        if not result.success:
            continue

        weights = result.x

        expected_return, volatility, sharpe_ratio = portfolio_performance(
            weights=weights,
            mean_returns=mean_returns,
            cov_matrix=cov_matrix,
            risk_free_rate=risk_free_rate,
        )

        row = {
            "expected_return": expected_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
        }

        for ticker, weight in zip(mean_returns.index, weights):
            row[ticker] = float(weight)

        frontier_rows.append(row)

    return pd.DataFrame(frontier_rows)
