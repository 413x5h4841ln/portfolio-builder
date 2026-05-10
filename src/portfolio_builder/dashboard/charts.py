# src/portfolio_builder/dashboard/charts.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _to_long_dataframe(
    df: pd.DataFrame,
    value_name: str,
    name_column: str = "name",
) -> pd.DataFrame:
    """
    Convert a wide DataFrame into long format for Plotly Express.
    """
    index_name = df.index.name or "date"

    long_df = (
        df.reset_index()
        .melt(
            id_vars=index_name,
            var_name=name_column,
            value_name=value_name,
        )
        .dropna()
    )

    return long_df


def plot_normalized_performance(
    normalized_performance: pd.DataFrame,
) -> go.Figure:
    """
    Plot normalized asset performance.
    """
    long_df = _to_long_dataframe(
        normalized_performance,
        value_name="cumulative_return",
        name_column="ticker",
    )

    fig = px.line(
        long_df,
        x=long_df.columns[0],
        y="cumulative_return",
        color="ticker",
        title="Normalized Stock Performance",
    )

    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(legend_title_text="Ticker")

    return fig


def plot_cumulative_returns(
    cumulative_returns: pd.DataFrame,
) -> go.Figure:
    """
    Plot cumulative returns for stocks and portfolios.
    """
    long_df = _to_long_dataframe(
        cumulative_returns,
        value_name="cumulative_return",
        name_column="series",
    )

    fig = px.line(
        long_df,
        x=long_df.columns[0],
        y="cumulative_return",
        color="series",
        title="Cumulative Returns",
    )

    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(legend_title_text="Series")

    return fig


def plot_drawdowns(
    drawdowns: pd.DataFrame,
) -> go.Figure:
    """
    Plot drawdowns.
    """
    long_df = _to_long_dataframe(
        drawdowns,
        value_name="drawdown",
        name_column="series",
    )

    fig = px.line(
        long_df,
        x=long_df.columns[0],
        y="drawdown",
        color="series",
        title="Drawdowns",
    )

    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(legend_title_text="Series")

    return fig


def plot_weights(
    weights: dict[str, float],
    title: str,
) -> go.Figure:
    """
    Plot portfolio weights as a bar chart.
    """
    df = pd.DataFrame(
        {
            "ticker": list(weights.keys()),
            "weight": list(weights.values()),
        }
    ).sort_values("weight", ascending=False)

    fig = px.bar(
        df,
        x="ticker",
        y="weight",
        title=title,
        text_auto=".1%",
    )

    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(showlegend=False)

    return fig


def plot_efficient_frontier(
    frontier: pd.DataFrame,
    max_sharpe_point: dict[str, float],
    min_volatility_point: dict[str, float],
) -> go.Figure:
    """
    Plot efficient frontier with highlighted optimized portfolios.
    """
    fig = px.scatter(
        frontier,
        x="volatility",
        y="expected_return",
        color="sharpe_ratio",
        title="Efficient Frontier",
        hover_data=frontier.columns,
    )

    fig.add_trace(
        go.Scatter(
            x=[max_sharpe_point["volatility"]],
            y=[max_sharpe_point["expected_return"]],
            mode="markers",
            marker={"size": 14, "symbol": "star"},
            name="Max Sharpe",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[min_volatility_point["volatility"]],
            y=[min_volatility_point["expected_return"]],
            mode="markers",
            marker={"size": 14, "symbol": "diamond"},
            name="Min Volatility",
        )
    )

    fig.update_xaxes(title="Annual Volatility", tickformat=".0%")
    fig.update_yaxes(title="Expected Annual Return", tickformat=".0%")

    return fig
