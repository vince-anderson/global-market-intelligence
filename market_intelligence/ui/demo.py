"""Explicitly selected offline demo workspace."""

import streamlit as st

from market_intelligence.data.demo import DEMO_END_DATE, DemoMarketDataProvider
from market_intelligence.research.modules import MODULE_BY_NAME
from market_intelligence.ui.charts import price_chart


def render_demo(section: str):
    provider = DemoMarketDataProvider()
    quotes = provider.snapshot()
    st.warning(f"模拟数据 · 非实时行情。固定演示终点 {DEMO_END_DATE}，全部价格由程序生成。")
    st.subheader("01 / 市场总览")
    for column, symbol in zip(st.columns(4), ("SPY", "QQQ", "BTC", "GLD")):
        row = quotes.set_index("symbol").loc[symbol]
        with column:
            st.metric(f"{symbol} · {row['name']}", f"${row['price']:,.2f}", f"{row['change_pct']:+.2f}%")
    st.caption("卡片变化 = 最后两个模拟自然日收盘价的变化；所有价格单位均为 USD。")

    if section != "市场总览":
        module = MODULE_BY_NAME[section]
        st.info(f"{module.name} / {module.description}。本阶段仅提供模拟观察界面；规划能力：{module.next_steps}。")
        if module.key == "tokenized":
            st.caption("带 -DEMO 的代码为虚构概念标识，不对应真实发行产品、交易场所或可交易合约。")
        if module.key == "macro":
            st.caption("GLD / TLT 为宏观资产代理示例，不是经济指标、利率或汇率原始数据。")
        if module.key == "quant":
            st.caption("当前未实现回测、因子模型或策略收益分析；下方仅演示资产价格。")

    focus = MODULE_BY_NAME[section].key if section in MODULE_BY_NAME else None
    available = quotes if focus in (None, "quant") else quotes[quotes["category"] == focus]
    left, right = st.columns([1, 1.65], gap="large")
    with left:
        st.subheader("02 / 资产观察列表")
        selected = st.multiselect(
            "观察资产", quotes["symbol"].tolist(), default=available["symbol"].tolist(),
            key=f"watchlist_{section}",
        )
        watched = quotes[quotes["symbol"].isin(selected)]
        if watched.empty:
            st.info("选择至少一个资产以填充观察列表。右侧图表可独立使用。")
        else:
            st.dataframe(
                watched[["symbol", "name", "price", "change_pct"]], hide_index=True,
                width="stretch", column_config={
                    "symbol": "资产", "name": "名称（模拟）",
                    "price": st.column_config.NumberColumn("模拟价格 / USD", format="$%.2f"),
                    "change_pct": st.column_config.NumberColumn("模拟日变化 / %", format="%+.2f%%"),
                },
            )
        st.caption("观察列表仅保留在当前会话；不保存持仓、账户或个人信息。")
    with right:
        st.subheader("03 / 行情走势图 · 模拟")
        controls = st.columns([2, 1])
        symbol = controls[0].selectbox("图表资产", available["symbol"].tolist(), key=f"chart_{section}")
        window = controls[1].selectbox("模拟区间", ["1M", "3M", "6M", "1Y"], index=1)
        days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}[window]
        st.plotly_chart(price_chart(provider.history(symbol), symbol, days), width="stretch")
        st.caption("滚动缩放、悬停查看模拟价格；区间为自然日数，非实际市场历史。")
