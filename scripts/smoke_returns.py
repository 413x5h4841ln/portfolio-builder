from portfolio_builder.data.price_service import get_price_history
from portfolio_builder.analytics.returns import (
    calculate_daily_returns,
    annualized_mean_returns,
    annualized_covariance,
)

prices = get_price_history(
    ["AAPL", "MSFT", "NVDA"],
    "2020-01-01",
    "2024-01-01",
)

returns = calculate_daily_returns(prices)

print(annualized_mean_returns(returns))
print(annualized_covariance(returns))
