import numpy as np
import pandas as pd
import pytest

from market_intelligence.data.demo import ASSETS, DEMO_END_DATE, DemoMarketDataProvider
from market_intelligence.research.modules import MODULES


def test_demo_history_is_reproducible_and_valid():
    provider = DemoMarketDataProvider()
    assert len({asset.symbol for asset in ASSETS}) == len(ASSETS)
    for asset in provider.assets():
        history = provider.history(asset.symbol)
        pd.testing.assert_frame_equal(history, DemoMarketDataProvider().history(asset.symbol))
        assert len(history) == 520
        assert history.date.is_monotonic_increasing
        assert history.date.is_unique
        assert str(history.date.iloc[-1].date()) == DEMO_END_DATE
        assert np.isfinite(history.close).all()
        assert history.close.gt(0).all()


def test_quotes_match_chart_and_daily_change():
    provider = DemoMarketDataProvider()
    for row in provider.snapshot().itertuples():
        prices = provider.history(row.symbol).close
        assert row.price == prices.iloc[-1]
        assert row.change_pct == pytest.approx((prices.iloc[-1] / prices.iloc[-2] - 1) * 100)
        assert row.currency == "USD"
    assert "模拟" in provider.source_label
    assert {a.category for a in ASSETS} <= {m.key for m in MODULES}


def test_unknown_asset_is_rejected():
    with pytest.raises(ValueError, match="Unknown demo asset"):
        DemoMarketDataProvider().history("INVALID")
