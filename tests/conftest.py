"""Offline synthetic HTTP fixtures; never represented as a live-provider test."""

from copy import deepcopy
from datetime import datetime, timezone

import pytest


def chart_payload(symbol="SPY"):
    times = [int(datetime(2026, 11, day, 14, 30, tzinfo=timezone.utc).timestamp()) for day in (11, 12, 13)]
    return {"chart": {"error": None, "result": [{
        "meta": {"symbol": symbol, "shortName": f"Fixture {symbol}", "currency": "USD",
                 "instrumentType": "ETF" if symbol in {"SPY", "QQQ", "DIA", "IWM"} else "EQUITY",
                 "exchangeTimezoneName": "America/New_York", "exchangeName": "NMS",
                 "exchangeDataDelayedBy": 15},
        "timestamp": times,
        "indicators": {"quote": [{"close": [100.0, 102.0, 105.0], "volume": [10, 20, 30]}]},
    }]}}


class FakeResponse:
    status_code = 200

    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return deepcopy(self.payload)


@pytest.fixture
def offline_app(monkeypatch):
    from market_intelligence.ui.live import load_market_data

    load_market_data.clear()
    calls = []

    def get(url, **kwargs):
        symbol = url.rsplit("/", 1)[-1]
        calls.append(symbol)
        return FakeResponse(chart_payload(symbol))

    monkeypatch.setattr("market_intelligence.data.yahoo.requests.get", get)
    yield calls
    load_market_data.clear()
