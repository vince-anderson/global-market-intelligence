"""Streamlit entry point: run with `streamlit run app.py`."""

import streamlit as st

from market_intelligence.research.modules import MODULE_BY_NAME, MODULES
from market_intelligence.ui.demo import render_demo
from market_intelligence.ui.live import render_live
from market_intelligence.ui.styles import TERMINAL_CSS

st.set_page_config(page_title="Global Market Intelligence", page_icon="◈", layout="wide")
st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ◈ GMI TERMINAL")
    st.caption("GLOBAL MARKET INTELLIGENCE")
    st.divider()
    section = st.radio("研究工作区", ["市场总览", *MODULE_BY_NAME], key="workspace")
    mode = st.radio("数据模式", ["真实美股 / ETF 日线", "模拟演示"], key="data_mode")
    auto_refresh = st.toggle("每 5 分钟自动检查", value=True, disabled=mode == "模拟演示")
    st.divider()
    st.caption("真实数据源：Yahoo Finance（聚合源，非交易所一手直连）")
    st.caption("无交易账户 · 无交易执行")
    st.caption("v0.2 / 开源研究辅助系统")

st.markdown('<div class="eyebrow">RESEARCH / CROSS-ASSET / OPEN SOURCE</div>', unsafe_allow_html=True)
st.title("全球市场，统一研究视角。")
st.markdown('<div class="subtitle">Global Market Intelligence · 从跨资产观察到可复现研究</div>', unsafe_allow_html=True)

if mode == "模拟演示":
    st.markdown('<span class="demo-badge">DEMO DATA / 模拟数据 · 非实时行情</span>', unsafe_allow_html=True)
    render_demo(section)
else:
    st.info("真实美股 / ETF · 最新可用日线 · 不保证实时")
    if section in ("市场总览", "美股"):
        render_live(auto_refresh)
    else:
        st.info("该研究模块尚未接入真实数据。本次仅接入美股和 ETF，请切换到美股工作区；模拟示例需在侧栏明确选择。")

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
st.caption("GMI / OPEN RESEARCH — 研究工具，不构成投资建议，不提供交易执行功能。")
