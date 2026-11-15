from datetime import datetime, timezone

import pytest
import requests

from conftest import FakeResponse, chart_payload
from market_intelligence.data.yahoo import MarketDataError, YahooMarketDataProvider, normalize_symbol, parse_chart

NOW = datetime(2026, 11, 16, tzinfo=timezone.utc)


def test_parses_source_dates_prices_and_volume():
    item = parse_chart("SPY", chart_payload(), NOW)
    assert item.price == 105
    assert item.change_pct == pytest.approx((105 / 102 - 1) * 100)
    assert item.as_of.isoformat() == "2026-11-13T09:30:00-05:00"
    assert item.fetched_at == NOW
    assert str(item.history.date.iloc[-1].date()) == "2026-11-13"
    assert list(item.history.volume) == [10, 20, 30]
    assert item.delay_minutes == 15


def test_invalid_prices_are_not_replaced_or_forward_filled():
    payload = chart_payload()
    payload["chart"]["result"][0]["indicators"]["quote"][0]["close"] = [100, None, 105]
    item = parse_chart("SPY", payload, NOW)
    assert len(item.history) == 2
    assert item.change_pct == pytest.approx(5)


@pytest.mark.parametrize("field,value", [
    ("currency", "EUR"), ("instrumentType", "CRYPTOCURRENCY"),
    ("exchangeTimezoneName", "Europe/London"), ("symbol", "MSFT"),
])
def test_wrong_instrument_metadata_is_rejected(field, value):
    payload = chart_payload()
    payload["chart"]["result"][0]["meta"][field] = value
    with pytest.raises(MarketDataError):
        parse_chart("SPY", payload, NOW)


@pytest.mark.parametrize("payload", [{}, {"chart": "invalid"}, {"chart": {"error": {"code": "Not Found"}}},
                                        {"chart": {"result": []}}])
def test_malformed_or_unknown_asset(payload):
    with pytest.raises(MarketDataError):
        parse_chart("INVALID", payload, NOW)


def test_sparse_history_and_length_mismatch():
    for close in ([None, None, 10], [100]):
        payload = chart_payload()
        payload["chart"]["result"][0]["indicators"]["quote"][0]["close"] = close
        with pytest.raises(MarketDataError):
            parse_chart("SPY", payload, NOW)


def test_symbol_normalization_and_injection_rejection():
    assert normalize_symbol(" brk-b ") == "BRK-B"
    for symbol in ("", "../../secret", "AAPL?range=1d", "BTC-USD/"):
        with pytest.raises(MarketDataError):
            normalize_symbol(symbol)


def test_timeout_and_rate_limit_are_explicit(monkeypatch):
    def timeout(*args, **kwargs):
        raise requests.Timeout()
    monkeypatch.setattr("market_intelligence.data.yahoo.requests.get", timeout)
    with pytest.raises(MarketDataError, match="请求失败"):
        YahooMarketDataProvider().fetch("SPY")
    response = FakeResponse({})
    response.status_code = 429
    monkeypatch.setattr("market_intelligence.data.yahoo.requests.get", lambda *a, **kw: response)
    with pytest.raises(MarketDataError, match="限流"):
        YahooMarketDataProvider().fetch("SPY")


def test_http_request_settings_and_partial_failure(monkeypatch):
    def get(url, **kwargs):
        assert url.startswith("https://query1.finance.yahoo.com/")
        assert kwargs["params"]["interval"] == "1d"
        assert kwargs["timeout"] == (3.05, 8)
        assert "verify" not in kwargs  # Requests retains certificate verification.
        symbol = url.rsplit("/", 1)[-1]
        return FakeResponse(chart_payload(symbol) if symbol != "INVALID" else {"chart": {"result": []}})
    monkeypatch.setattr("market_intelligence.data.yahoo.requests.get", get)
    series, errors = YahooMarketDataProvider().fetch_many(("SPY", "INVALID"))
    assert set(series) == {"SPY"}
    assert set(errors) == {"INVALID"}


def test_missing_timestamps_and_duplicate_days():
    payload = chart_payload()
    result = payload["chart"]["result"][0]
    result["timestamp"][1] = None
    item = parse_chart("SPY", payload, NOW)
    assert len(item.history) == 2
    assert item.change_pct == pytest.approx(5)
    result["timestamp"][1] = result["timestamp"][0]
    item = parse_chart("SPY", payload, NOW)
    assert len(item.history) == 2
    assert item.history.date.is_unique
