from pathlib import Path

import requests
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_real_home_cache_and_manual_refresh(offline_app):
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.exception
    assert len(app.metric) == 4
    assert len(app.dataframe) == 1
    assert len(app.get("plotly_chart")) == 1
    assert all(item.value != "暂无数据" for item in app.metric)
    assert any("真实美股" in item.value for item in app.info)
    assert not any("DEMO DATA" in item.value for item in app.markdown)
    count = len(offline_app)
    app.selectbox(key="live_window").select("1Y").run()
    assert not app.exception
    assert len(offline_app) == count
    app.button(key="refresh_market").click().run()
    assert not app.exception
    assert len(offline_app) > count
    assert any("抓取时间" in item.value for item in app.caption)


def test_add_custom_symbol_and_empty_watchlist(offline_app):
    app = AppTest.from_file(str(APP)).run(timeout=30)
    app.text_input[0].set_value("amd")
    next(button for button in app.button if button.label == "添加代码").click().run()
    assert not app.exception
    assert "AMD" in app.multiselect[0].value
    assert "AMD" in offline_app
    app.multiselect[0].set_value([]).run()
    assert not app.exception
    assert not app.dataframe
    assert len(app.get("plotly_chart")) == 1


def test_failure_never_falls_back_to_demo(offline_app, monkeypatch):
    def timeout(*args, **kwargs):
        raise requests.Timeout()
    monkeypatch.setattr("market_intelligence.data.yahoo.requests.get", timeout)
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.exception
    assert app.error
    assert not app.metric
    assert not app.get("plotly_chart")
    assert any("不会以模拟数据填充" in item.value for item in app.info)


def test_demo_mode_and_navigation(offline_app):
    app = AppTest.from_file(str(APP)).run(timeout=30)
    app.radio(key="data_mode").set_value("模拟演示").run()
    assert not app.exception
    assert len(app.metric) == 4
    assert any("非实时行情" in item.value for item in app.markdown)
    for section in ("美股", "代币化美股", "加密货币", "全球宏观", "量化研究"):
        app.radio(key="workspace").set_value(section).run()
        assert not app.exception
        assert len(app.get("plotly_chart")) == 1
    app.button(key="open_crypto").click().run()
    assert not app.exception
    assert app.radio(key="workspace").value == "加密货币"
    assert app.selectbox[0].options == ["BTC", "ETH"]
    app.radio(key="data_mode").set_value("真实美股 / ETF 日线").run()
    assert not app.exception
    assert not app.metric
    assert not app.get("plotly_chart")
