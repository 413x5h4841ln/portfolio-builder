from portfolio_builder.analytics.returns import (
    annualized_covariance,
    annualized_mean_returns,
    calculate_daily_returns,
)
from portfolio_builder.data.price_service import get_price_history

prices = get_price_history(
    ["AAPL", "MSFT", "NVDA"],
    "2020-01-01",
    "2024-01-01",
)

returns = calculate_daily_returns(prices)

print(annualized_mean_returns(returns))
print(annualized_covariance(returns))
