# src/portfolio_builder/cli.py

from portfolio_builder.analytics.optimizer import (
    efficient_frontier,
    max_sharpe_portfolio,
    min_volatility_portfolio,
)
from portfolio_builder.analytics.performance import (
    compare_metrics,
    compare_return_series,
    cumulative_returns,
    normalized_price_performance,
)
from portfolio_builder.analytics.portfolio import equal_weight_portfolio
from portfolio_builder.analytics.returns import (
    annualized_covariance,
    annualized_mean_returns,
    calculate_daily_returns,
)
from portfolio_builder.data.price_service import get_price_history


def print_portfolio(name, portfolio) -> None:
    print(f"\n{name}")
    print("-" * len(name))

    print("Weights:")
    for ticker, weight in portfolio.weights.items():
        print(f"  {ticker}: {weight:.2%}")

    print(f"Expected annual return: {portfolio.expected_return:.2%}")
    print(f"Annual volatility:      {portfolio.volatility:.2%}")
    print(f"Sharpe ratio:           {portfolio.sharpe_ratio:.2f}")


def main() -> None:
    tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"]
    start_date = "2020-01-01"
    end_date = "2024-01-01"
    risk_free_rate = 0.02

    prices = get_price_history(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
    )

    daily_returns = calculate_daily_returns(prices)

    mean_returns = annualized_mean_returns(daily_returns)
    cov_matrix = annualized_covariance(daily_returns)

    equal_weight = equal_weight_portfolio(tickers)

    max_sharpe = max_sharpe_portfolio(
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
    )

    min_vol = min_volatility_portfolio(
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
    )

    frontier = efficient_frontier(
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
        points=30,
    )

    portfolios = {
        "Equal Weight": equal_weight,
        "Max Sharpe": max_sharpe.weights,
        "Min Volatility": min_vol.weights,
    }

    portfolio_returns = compare_return_series(
        daily_returns=daily_returns,
        portfolios=portfolios,
    )

    all_returns = daily_returns.join(portfolio_returns)

    metrics = compare_metrics(
        return_series=all_returns,
        risk_free_rate=risk_free_rate,
    )

    cumulative = cumulative_returns(all_returns)

    normalized_stocks = normalized_price_performance(prices)

    print("\nPrice Data")
    print("----------")
    print(prices.head())
    print()
    print(f"Rows: {len(prices)}")

    print_portfolio("Max Sharpe Portfolio", max_sharpe)
    print_portfolio("Min Volatility Portfolio", min_vol)

    print("\nPerformance Comparison")
    print("----------------------")
    print(
        metrics.sort_values("sharpe_ratio", ascending=False).to_string(
            formatters={
                "total_return": "{:.2%}".format,
                "annual_return": "{:.2%}".format,
                "annual_volatility": "{:.2%}".format,
                "sharpe_ratio": "{:.2f}".format,
                "max_drawdown": "{:.2%}".format,
            }
        )
    )

    print("\nCumulative Returns")
    print("------------------")
    print(cumulative.tail())

    print("\nNormalized Stock Performance")
    print("----------------------------")
    print(normalized_stocks.tail())

    print("\nEfficient Frontier")
    print("------------------")
    print(frontier.head())
    print()
    print(f"Generated {len(frontier)} frontier portfolios.")


if __name__ == "__main__":
    main()
