"""Streamlit entry point: run with `streamlit run app.py`."""

import streamlit as st

from market_intelligence.data.demo import DEMO_END_DATE, DemoMarketDataProvider
from market_intelligence.research.modules import MODULE_BY_NAME, MODULES
from market_intelligence.ui.charts import price_chart
from market_intelligence.ui.styles import TERMINAL_CSS

st.set_page_config(page_title="Global Market Intelligence", page_icon="◈", layout="wide")
st.markdown(TERMINAL_CSS, unsafe_allow_html=True)
provider = DemoMarketDataProvider()
quotes = provider.snapshot()

with st.sidebar:
    st.markdown("### ◈ GMI TERMINAL")
    st.caption("GLOBAL MARKET INTELLIGENCE")
    st.divider()
    section = st.radio("研究工作区", ["市场总览", *MODULE_BY_NAME], key="workspace")
    st.divider()
    st.markdown("**数据模式：模拟 / DEMO**")
    st.caption(f"固定演示终点：{DEMO_END_DATE}，非当前行情。")
    st.caption("无行情 API · 无交易账户 · 无交易执行")
    st.caption("v0.1 / 开源研究辅助系统")

st.markdown('<div class="eyebrow">RESEARCH / CROSS-ASSET / OPEN SOURCE</div>', unsafe_allow_html=True)
st.title("全球市场，统一研究视角。")
st.markdown('<div class="subtitle">Global Market Intelligence · 从跨资产观察到可复现研究</div>', unsafe_allow_html=True)
st.markdown('<span class="demo-badge">DEMO DATA / 模拟数据 · 非实时行情</span>', unsafe_allow_html=True)
st.caption(
    f"全部价格与涨跌幅由固定种子生成，演示终点 {DEMO_END_DATE}；"
    "使用连续自然日，非交易所日历。资产代码仅供界面演示，不代表真实报价或投资建议。"
)

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

st.divider()
st.subheader("04 / 研究模块")
for module, column in zip(MODULES, st.columns(len(MODULES))):
    with column:
        with st.container(border=True):
            st.markdown(f"**{module.name}**")
            st.caption(module.description)
            st.caption(f"规划：{module.next_steps}")
            st.button(
                "打开工作区", key=f"open_{module.key}", width="stretch",
                on_click=lambda name=module.name: st.session_state.update(workspace=name),
            )
st.caption("GMI / OPEN RESEARCH — 模拟数据演示。研究工具，不提供交易执行功能。")
