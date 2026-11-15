"""Pure Plotly builders, usable without a running Streamlit server."""

import pandas as pd
import plotly.graph_objects as go


def price_chart(history: pd.DataFrame, symbol: str, days: int) -> go.Figure:
    if days < 2:
        raise ValueError("Chart window must contain at least two days")
    data = history.tail(days)
    if data.empty:
        raise ValueError("Price history is empty")
    fig = go.Figure(go.Scatter(
        x=data["date"], y=data["close"], mode="lines", name=symbol,
        line={"color": "#39d7bc", "width": 2},
        fill="tozeroy", fillcolor="rgba(57,215,188,0.055)",
        hovertemplate="%{x|%Y-%m-%d}<br>$%{y:,.2f}<extra>模拟收盘价</extra>",
    ))
    fig.update_layout(
        template="plotly_dark", height=390, showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 8, "r": 8, "t": 20, "b": 8}, hovermode="x unified",
        font={"color": "#9aabc0"},
        xaxis={"showgrid": False, "title": None},
        yaxis={"gridcolor": "#1d293b", "title": "模拟价格 / USD", "side": "right", "rangemode": "normal"},
        title={"text": f"{symbol} · 模拟数据", "font": {"size": 13}},
    )
    # Explicit padded range preserves useful price variation despite the area fill.
    low, high = data["close"].min(), data["close"].max()
    padding = max((high - low) * 0.12, high * 0.005)
    fig.update_yaxes(range=[low - padding, high + padding])
    return fig
