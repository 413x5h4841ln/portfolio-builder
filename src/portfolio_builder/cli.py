# src/portfolio_builder/cli.py

from portfolio_builder.data.price_service import get_price_history
from portfolio_builder.analytics.returns import calculate_daily_returns
from portfolio_builder.analytics.portfolio import (
    equal_weight_portfolio,
    portfolio_returns,
    portfolio_metrics,
)
prices = get_price_history(
    tickers=["AAPL", "MSFT", "NVDA"],
    start_date="2020-01-01",
    end_date="2024-01-01",
)

print(prices.head())
print()
print(prices.tail())
print()
print(prices.shape)

tickers = ["AAPL", "MSFT", "NVDA"]

prices = get_price_history(tickers, "2020-01-01", "2024-01-01")
daily_returns = calculate_daily_returns(prices)

weights = equal_weight_portfolio(tickers)
port_returns = portfolio_returns(daily_returns, weights)
metrics = portfolio_metrics(port_returns, risk_free_rate=0.02)

print("Weights:")
print(weights)

print("\nMetrics:")
print(metrics)
