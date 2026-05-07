from portfolio_builder.data.price_service import get_price_history

prices = get_price_history(
    tickers=["AAPL", "MSFT", "NVDA"],
    start_date="2020-01-01",
    end_date="2024-01-01",
)

print(prices.head())

# Expected output:


#                  AAPL        MSFT        NVDA
#Date                                          
#2020-01-02   72.796021  154.493835    5.972711
#2020-01-03   72.088303  152.570129    5.877112
#...


