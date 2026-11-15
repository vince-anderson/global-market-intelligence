import pytest

from market_intelligence.data.demo import DemoMarketDataProvider
from market_intelligence.ui.charts import price_chart


@pytest.mark.parametrize("days", [30, 90, 180, 365])
def test_chart_window_and_source_label(days):
    history = DemoMarketDataProvider().history("SPY")
    chart = price_chart(history, "SPY", days)
    assert len(chart.data[0].x) == days
    assert list(chart.data[0].y) == list(history.tail(days).close)
    assert "模拟" in chart.layout.title.text
    assert "USD" in chart.layout.yaxis.title.text


def test_invalid_window():
    with pytest.raises(ValueError):
        price_chart(DemoMarketDataProvider().history("SPY"), "SPY", 0)
