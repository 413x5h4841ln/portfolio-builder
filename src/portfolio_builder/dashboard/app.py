# src/portfolio_builder/dashboard/app.py

from datetime import date, timedelta

import pandas as pd
from pandas.io.formats.style import Styler

import streamlit as st

from portfolio_builder.analytics.optimizer import (
    efficient_frontier,
    max_sharpe_portfolio,
    min_volatility_portfolio,
)
from portfolio_builder.analytics.performance import (
    compare_metrics,
    compare_return_series,
    cumulative_returns,
    drawdown_series,
    normalized_price_performance,
)
from portfolio_builder.analytics.portfolio import equal_weight_portfolio
from portfolio_builder.analytics.returns import (
    annualized_covariance,
    annualized_mean_returns,
    calculate_daily_returns,
)
from portfolio_builder.dashboard.charts import (
    plot_cumulative_returns,
    plot_drawdowns,
    plot_efficient_frontier,
    plot_normalized_performance,
    plot_weights,
)
from portfolio_builder.data.price_service import get_cache_summary, get_price_history


def parse_tickers(raw_tickers: str) -> list[str]:
    """
    Parse user ticker input.

    Accepts:
        AAPL, MSFT, NVDA
        AAPL MSFT NVDA
    """
    cleaned = raw_tickers.replace(",", " ")
    tickers = [ticker.upper().strip() for ticker in cleaned.split()]
    return sorted(set(ticker for ticker in tickers if ticker))


def format_metrics(metrics: pd.DataFrame) -> Styler:
    """
    Format the metrics table for Streamlit.
    """
    return metrics.style.format(
        {
            "total_return": "{:.2%}",
            "annual_return": "{:.2%}",
            "annual_volatility": "{:.2%}",
            "sharpe_ratio": "{:.2f}",
            "max_drawdown": "{:.2%}",
        }
    )


@st.cache_data(show_spinner=False)
def run_analysis(
    tickers: tuple[str, ...],
    start_date: date,
    end_date: date,
    risk_free_rate: float,
    max_weight: float,
    frontier_points: int,
) -> dict:
    """
    Run the full portfolio analysis.

    The dashboard treats end_date as inclusive, while the data layer treats
    end_date as exclusive, so we add one day here.
    """
    end_date_exclusive = end_date + timedelta(days=1)

    prices = get_price_history(
        tickers=list(tickers),
        start_date=start_date,
        end_date=end_date_exclusive,
    )

    prices = prices.dropna(how="all")

    if prices.empty:
        raise ValueError("No price data returned for the selected inputs.")

    daily_returns = calculate_daily_returns(prices).dropna(how="any")

    if daily_returns.empty:
        raise ValueError("Not enough price data to calculate returns.")

    mean_returns = annualized_mean_returns(daily_returns)
    cov_matrix = annualized_covariance(daily_returns)

    equal_weight = equal_weight_portfolio(list(daily_returns.columns))

    max_sharpe = max_sharpe_portfolio(
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
        min_weight=0.0,
        max_weight=max_weight,
    )

    min_volatility = min_volatility_portfolio(
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
        min_weight=0.0,
        max_weight=max_weight,
    )

    frontier = efficient_frontier(
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
        points=frontier_points,
        min_weight=0.0,
        max_weight=max_weight,
    )

    portfolios = {
        "Equal Weight": equal_weight,
        "Max Sharpe": max_sharpe.weights,
        "Min Volatility": min_volatility.weights,
    }

    portfolio_returns = compare_return_series(
        daily_returns=daily_returns,
        portfolios=portfolios,
    )

    all_returns = daily_returns.join(portfolio_returns)

    metrics = compare_metrics(
        return_series=all_returns,
        risk_free_rate=risk_free_rate,
    ).sort_values("sharpe_ratio", ascending=False)

    cumulative = cumulative_returns(all_returns)

    drawdowns = pd.DataFrame(
        {
            column: drawdown_series(all_returns[column].dropna())
            for column in all_returns.columns
        }
    )

    normalized_stocks = normalized_price_performance(prices)

    return {
        "prices": prices,
        "daily_returns": daily_returns,
        "mean_returns": mean_returns,
        "cov_matrix": cov_matrix,
        "max_sharpe": max_sharpe,
        "min_volatility": min_volatility,
        "frontier": frontier,
        "portfolio_returns": portfolio_returns,
        "all_returns": all_returns,
        "metrics": metrics,
        "cumulative": cumulative,
        "drawdowns": drawdowns,
        "normalized_stocks": normalized_stocks,
    }


def main() -> None:
    st.set_page_config(
        page_title="Portfolio Builder",
        page_icon="📈",
        layout="wide",
    )

    st.title("📈 Portfolio Builder")
    st.caption(
        "Historical prices, Markowitz-style optimization, performance comparison, "
        "and efficient frontier visualization."
    )

    with st.sidebar:
        st.header("Inputs")

        raw_tickers = st.text_input(
            "Tickers",
            value="AAPL, MSFT, NVDA, GOOGL, AMZN",
            help="Use commas or spaces between tickers.",
        )

        start_date = st.date_input(
            "Start date",
            value=date(2020, 1, 1),
        )

        end_date = st.date_input(
            "End date",
            value=date(2024, 1, 1),
        )

        risk_free_rate_percent = st.number_input(
            "Risk-free rate (%)",
            value=2.0,
            min_value=0.0,
            max_value=20.0,
            step=0.25,
        )

        max_weight_percent = st.slider(
            "Max weight per asset (%)",
            min_value=5,
            max_value=100,
            value=100,
            step=5,
        )

        frontier_points = st.slider(
            "Efficient frontier points",
            min_value=10,
            max_value=100,
            value=40,
            step=5,
        )

        run_button = st.button("Run analysis", type="primary")

        if st.button("Clear dashboard cache"):
            st.cache_data.clear()
            st.success("Dashboard cache cleared.")

    tickers = parse_tickers(raw_tickers)
    risk_free_rate = risk_free_rate_percent / 100
    max_weight = max_weight_percent / 100

    if len(tickers) < 2:
        st.warning("Enter at least two tickers.")
        return

    if start_date >= end_date:
        st.warning("Start date must be before end date.")
        return

    if max_weight * len(tickers) < 1:
        st.warning(
            "Max weight is too restrictive. "
            "Increase max weight or reduce the number of tickers."
        )
        return

    if not run_button:
        st.info("Choose inputs in the sidebar and click **Run analysis**.")
        with st.expander("Cached data summary"):
            cache_summary = get_cache_summary()
            if cache_summary.empty:
                st.write("No cached data yet.")
            else:
                st.dataframe(cache_summary, use_container_width=True)
        return

    try:
        with st.spinner("Running portfolio analysis..."):
            result = run_analysis(
                tickers=tuple(tickers),
                start_date=start_date,
                end_date=end_date,
                risk_free_rate=risk_free_rate,
                max_weight=max_weight,
                frontier_points=frontier_points,
            )

    except Exception as error:
        st.error(f"Analysis failed: {error}")
        return

    prices = result["prices"]
    metrics = result["metrics"]
    max_sharpe = result["max_sharpe"]
    min_volatility = result["min_volatility"]
    frontier = result["frontier"]

    st.subheader("Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tickers", len(prices.columns))
    col2.metric("Price rows", len(prices))
    col3.metric("Best Sharpe", f"{metrics['sharpe_ratio'].max():.2f}")
    col4.metric(
        "Best total return",
        f"{metrics['total_return'].max():.2%}",
    )

    st.subheader("Performance Metrics")
    st.dataframe(
        format_metrics(metrics),
        use_container_width=True,
    )

    st.subheader("Optimized Portfolios")

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            plot_weights(
                max_sharpe.weights,
                title="Max Sharpe Portfolio Weights",
            ),
            use_container_width=True,
        )

        st.write(
            {
                "expected_annual_return": f"{max_sharpe.expected_return:.2%}",
                "annual_volatility": f"{max_sharpe.volatility:.2%}",
                "sharpe_ratio": f"{max_sharpe.sharpe_ratio:.2f}",
            }
        )

    with right:
        st.plotly_chart(
            plot_weights(
                min_volatility.weights,
                title="Min Volatility Portfolio Weights",
            ),
            use_container_width=True,
        )

        st.write(
            {
                "expected_annual_return": f"{min_volatility.expected_return:.2%}",
                "annual_volatility": f"{min_volatility.volatility:.2%}",
                "sharpe_ratio": f"{min_volatility.sharpe_ratio:.2f}",
            }
        )

    st.subheader("Charts")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Stocks",
            "Cumulative Returns",
            "Drawdowns",
            "Efficient Frontier",
        ]
    )

    with tab1:
        st.plotly_chart(
            plot_normalized_performance(result["normalized_stocks"]),
            use_container_width=True,
        )

    with tab2:
        st.plotly_chart(
            plot_cumulative_returns(result["cumulative"]),
            use_container_width=True,
        )

    with tab3:
        st.plotly_chart(
            plot_drawdowns(result["drawdowns"]),
            use_container_width=True,
        )

    with tab4:
        if frontier.empty:
            st.warning("No efficient frontier points were generated.")
        else:
            st.plotly_chart(
                plot_efficient_frontier(
                    frontier=frontier,
                    max_sharpe_point={
                        "volatility": max_sharpe.volatility,
                        "expected_return": max_sharpe.expected_return,
                    },
                    min_volatility_point={
                        "volatility": min_volatility.volatility,
                        "expected_return": min_volatility.expected_return,
                    },
                ),
                use_container_width=True,
            )

            st.dataframe(
                frontier.style.format(
                    {
                        "expected_return": "{:.2%}",
                        "volatility": "{:.2%}",
                        "sharpe_ratio": "{:.2f}",
                    }
                ),
                use_container_width=True,
            )

    with st.expander("Raw price data"):
        st.dataframe(prices, use_container_width=True)

    with st.expander("Cached data summary"):
        cache_summary = get_cache_summary()
        if cache_summary.empty:
            st.write("No cached data yet.")
        else:
            st.dataframe(cache_summary, use_container_width=True)


if __name__ == "__main__":
    main()
