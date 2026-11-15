"""US stock / ETF workspace with bounded caching and active-session refresh."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from market_intelligence.data.yahoo import SOURCE, MarketDataError, YahooMarketDataProvider, normalize_symbol
from market_intelligence.ui.charts import price_chart

OVERVIEW = ("SPY", "QQQ", "DIA", "IWM")
CATALOG = (*OVERVIEW, "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA",
           "VOO", "VTI", "VT", "VEA", "VWO", "GLD", "TLT", "BND", "XLK")
DEFAULT_WATCHLIST = [*OVERVIEW, "AAPL", "MSFT", "NVDA"]


@st.cache_data(ttl=300, max_entries=64, show_spinner=False)
def load_market_data(symbols: tuple[str, ...]):
    results, errors = YahooMarketDataProvider().fetch_many(symbols)
    if not results:
        # Exceptions are not cached; the user can retry without waiting for TTL.
        raise MarketDataError("；".join(errors.values()) or "数据源暂无可用行情。")
    return results, errors


def render_live(auto_refresh: bool):
    @st.fragment(run_every=300 if auto_refresh else None)
    def workspace():
        st.caption(f"来源：{SOURCE}。最新可用日线，不保证实时；当日尚未收盘时最后一条日线可能变化。")
        st.session_state.setdefault("live_watchlist", DEFAULT_WATCHLIST.copy())
        with st.form("add_symbol", clear_on_submit=True):
            entry, submit = st.columns([4, 1])
            custom = entry.text_input("添加美股 / ETF 代码", placeholder="例如 AMD、VOO、BRK-B")
            add = submit.form_submit_button("添加代码")
        extras = st.session_state.setdefault("extra_symbols", [])
        if add:
            try:
                symbol = normalize_symbol(custom)
                if symbol not in CATALOG and symbol not in extras:
                    if len(extras) >= 20:
                        raise MarketDataError("当前会话最多添加 20 个自定义代码。")
                    extras.append(symbol)
                watched = st.session_state.get("live_watchlist", DEFAULT_WATCHLIST.copy())
                if symbol not in watched:
                    if len(watched) >= 8:
                        st.warning("代码已加入候选列表；请先移除一个观察资产，再选入新代码（最多 8 个）。")
                    else:
                        st.session_state.live_watchlist = [*watched, symbol]
            except MarketDataError as exc:
                st.warning(str(exc))
        selected = st.multiselect(
            "美股与 ETF 观察列表（最多 8 个）", [*CATALOG, *extras],
            max_selections=8, key="live_watchlist",
        )
        symbols = tuple(sorted(set(OVERVIEW) | set(selected)))
        if st.button("立即刷新行情", key="refresh_market"):
            load_market_data.clear(symbols)
        st.caption("自动更新：页面活跃时每 5 分钟检查；缓存最长 5 分钟。页面休眠 / 关闭后不会持续抓取。")
        try:
            with st.spinner("正在获取美股 / ETF 日线…"):
                series, errors = load_market_data(symbols)
        except MarketDataError as exc:
            st.error(str(exc))
            st.info("暂时无法获取真实行情。不会以模拟数据填充；可重试，或在侧栏明确切换到模拟演示。")
            return
        for error in errors.values():
            st.warning(error)

        st.subheader("01 / 美股与 ETF 市场总览")
        for column, symbol in zip(st.columns(4), OVERVIEW):
            item = series.get(symbol)
            with column:
                st.metric(symbol, f"${item.price:,.2f}" if item else "暂无数据",
                          f"{item.change_pct:+.2f}%" if item else None)
                if item:
                    st.caption(f"日线日期：{item.as_of:%Y-%m-%d}（纽约）")
        st.caption("变化 = 最后两条有效交易日日线价格的变化，不包含分红收益；不是逐笔行情或盘前盘后报价。")
        left, right = st.columns([1, 1.65], gap="large")
        with left:
            st.subheader("02 / 真实资产观察列表")
            rows = [{"资产": symbol, "名称": series[symbol].name,
                     "价格 / USD": series[symbol].price, "日线变化 / %": series[symbol].change_pct,
                     "日线日期（纽约）": series[symbol].as_of.strftime("%Y-%m-%d")}
                    for symbol in selected if symbol in series]
            if rows:
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", column_config={
                    "价格 / USD": st.column_config.NumberColumn(format="$%.2f"),
                    "日线变化 / %": st.column_config.NumberColumn(format="%+.2f%%"),
                })
            else:
                st.info("观察列表暂无可用数据，请选择资产。右侧图表可独立使用。")
        with right:
            st.subheader("03 / 真实日线走势图")
            controls = st.columns([2, 1])
            symbol = controls[0].selectbox("图表资产", [s for s in symbols if s in series], key="live_chart")
            window = controls[1].selectbox("历史区间", ["1M", "3M", "6M", "1Y"], index=1, key="live_window")
            item = series[symbol]
            days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}[window]
            st.plotly_chart(price_chart(item.history, symbol, days, source_label="Yahoo Finance 日线"), width="stretch")
            st.caption(f"交易所：{item.exchange} · 币种：{item.currency} · 交易所时区：{item.exchange_timezone}")
            st.caption(f"日线记录时间：{item.as_of:%Y-%m-%d %H:%M %Z}（非逐笔报价时间）")
            fetched = item.fetched_at.astimezone(ZoneInfo("Asia/Shanghai"))
            st.caption(f"抓取时间：{fetched:%Y-%m-%d %H:%M:%S} UTC+8")
            delay = f"{item.delay_minutes} 分钟（数据源报告值，不代表端到端延迟保证）" if item.delay_minutes is not None else "未披露，不能视为实时行情"
            st.caption(f"行情延迟：{delay}")
            # Warn on obviously old bars without claiming a trading-calendar calculation.
            age = (datetime.now(timezone.utc) - item.as_of).total_seconds() / 86400
            if age > 4:
                st.warning("最后一条日线距今已超过 4 天，请核对休市、停牌或数据源更新情况；刷新时间不等于行情时间。")
            st.caption("价格日线未经本系统复权；以数据源返回值为准，不用于总回报或策略回测。区间按自然日截取，可能因上市时间而不足。")
    workspace()
