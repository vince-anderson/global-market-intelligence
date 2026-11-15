from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_home_and_interactions():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.exception
    assert len(app.metric) == 4
    assert len(app.dataframe) == 1
    assert len(app.get("plotly_chart")) == 1
    assert any("非实时行情" in item.value for item in app.markdown)
    app.selectbox[0].select("BTC").run()
    app.selectbox[1].select("1Y").run()
    assert not app.exception
    assert app.selectbox[0].value == "BTC"
    app.multiselect[0].set_value([]).run()
    assert not app.exception
    assert not app.dataframe
    assert any("选择至少一个资产" in item.value for item in app.info)


def test_all_workspaces_and_navigation():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    for section in ("美股", "代币化美股", "加密货币", "全球宏观", "量化研究"):
        app.radio[0].set_value(section).run()
        assert not app.exception
        assert app.info
        assert len(app.get("plotly_chart")) == 1
    app.button(key="open_crypto").click().run()
    assert not app.exception
    assert app.radio[0].value == "加密货币"
    assert app.selectbox[0].options == ["BTC", "ETH"]
