"""Deterministic synthetic fixtures. No network requests or real market quotes."""

import hashlib

import numpy as np
import pandas as pd

from market_intelligence.data.models import Asset

DEMO_END_DATE = "2026-01-30"
DEMO_LABEL = "模拟数据 · 非实时行情"
ASSETS = (
    Asset("SPY", "标普 500 ETF", "equities", 590, 0.009),
    Asset("QQQ", "纳斯达克 100 ETF", "equities", 515, 0.012),
    Asset("AAPL", "Apple", "equities", 230, 0.016),
    Asset("NVDA", "NVIDIA", "equities", 145, 0.025),
    Asset("AAPL-DEMO", "Apple 代币概念示例", "tokenized", 230, 0.018),
    Asset("SPY-DEMO", "指数代币概念示例", "tokenized", 590, 0.012),
    Asset("BTC", "Bitcoin", "crypto", 98000, 0.027),
    Asset("ETH", "Ethereum", "crypto", 3400, 0.035),
    Asset("GLD", "黄金 ETF · 宏观代理", "macro", 260, 0.010),
    Asset("TLT", "长期美债 ETF · 宏观代理", "macro", 90, 0.009),
)


class DemoMarketDataProvider:
    source_label = DEMO_LABEL

    def assets(self) -> tuple[Asset, ...]:
        return ASSETS

    def history(self, symbol: str) -> pd.DataFrame:
        asset = next((item for item in ASSETS if item.symbol == symbol), None)
        if asset is None:
            raise ValueError(f"Unknown demo asset: {symbol}")
        # A stable per-symbol seed keeps chart values unchanged across reruns/processes.
        seed = int.from_bytes(hashlib.sha256(symbol.encode()).digest()[:8], "big")
        rng = np.random.default_rng(seed)
        dates = pd.date_range(end=DEMO_END_DATE, periods=520, freq="D")
        returns = rng.normal(0.00035, asset.daily_volatility, len(dates))
        prices = asset.reference_price * np.exp(np.cumsum(returns))
        return pd.DataFrame({"date": dates, "close": prices})

    def snapshot(self) -> pd.DataFrame:
        rows = []
        for asset in ASSETS:
            close = self.history(asset.symbol)["close"]
            rows.append({
                "symbol": asset.symbol,
                "name": asset.name,
                "category": asset.category,
                "currency": asset.currency,
                "price": float(close.iloc[-1]),
                "change_pct": float((close.iloc[-1] / close.iloc[-2] - 1) * 100),
            })
        return pd.DataFrame(rows)
