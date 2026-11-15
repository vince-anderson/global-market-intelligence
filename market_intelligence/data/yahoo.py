"""Keyless Yahoo chart adapter for research. Unofficial, potentially delayed data."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
import re

import numpy as np
import pandas as pd
import requests

SOURCE = "Yahoo Finance · 公开聚合数据（非交易所直连）"
ENDPOINT = "https://query1.finance.yahoo.com/v8/finance/chart/"
SYMBOL_PATTERN = re.compile(r"^[A-Z][A-Z0-9.-]{0,14}$")


class MarketDataError(Exception):
    """A safe, actionable error that may be shown in the UI."""


@dataclass
class MarketSeries:
    symbol: str
    name: str
    currency: str
    exchange: str
    exchange_timezone: str
    as_of: datetime
    fetched_at: datetime
    history: pd.DataFrame
    delay_minutes: int | None

    @property
    def price(self) -> float:
        return float(self.history.close.iloc[-1])

    @property
    def change_pct(self) -> float:
        return float((self.history.close.iloc[-1] / self.history.close.iloc[-2] - 1) * 100)


def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.fullmatch(symbol):
        raise MarketDataError("请输入有效的美股 / ETF 代码，例如 AAPL、SPY 或 BRK-B。")
    return symbol


def parse_chart(symbol: str, payload: dict, fetched_at: datetime) -> MarketSeries:
    """Validate untrusted provider output and retain the actual source timestamps."""
    try:
        chart = payload["chart"]
        if chart.get("error") or not chart.get("result"):
            raise MarketDataError(f"{symbol}：数据源未返回行情，请检查代码或稍后重试。")
        result = chart["result"][0]
        meta = result["meta"]
        if meta["symbol"].upper() != symbol:
            raise MarketDataError(f"{symbol}：返回的资产代码不匹配。")
        if (meta.get("instrumentType") not in {"EQUITY", "ETF"}
                or meta.get("currency") != "USD"
                or meta.get("exchangeTimezoneName") != "America/New_York"):
            raise MarketDataError(f"{symbol}：本入口仅支持美元计价的美国股票和 ETF。")
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
        close = pd.to_numeric(pd.Series(quote["close"]), errors="coerce")
        if len(timestamps) != len(close):
            raise MarketDataError(f"{symbol}：日线时间和价格长度不一致。")
        times = pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(meta["exchangeTimezoneName"])
        frame = pd.DataFrame({"timestamp": times, "close": close.to_numpy()})
        frame = frame[frame.timestamp.notna() & np.isfinite(frame.close) & frame.close.gt(0)]
        frame = frame.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
        # Date axis reflects exchange-local dates, not the user's browser timezone.
        frame["date"] = frame.timestamp.dt.tz_localize(None).dt.normalize()
        frame = frame.drop_duplicates("date", keep="last").reset_index(drop=True)
        if len(frame) < 2:
            raise MarketDataError(f"{symbol}：有效日线不足两条，无法计算涨跌幅。")
        volume = quote.get("volume")
        if volume is not None and len(volume) == len(timestamps):
            volumes = pd.Series(pd.to_numeric(volume, errors="coerce"), index=times)
            frame["volume"] = frame.timestamp.map(volumes[~volumes.index.duplicated(keep="last")])
        delay = meta.get("exchangeDataDelayedBy")
        return MarketSeries(
            symbol=symbol, name=meta.get("longName") or meta.get("shortName") or symbol,
            currency="USD", exchange=meta.get("fullExchangeName") or meta.get("exchangeName", "未知"),
            exchange_timezone=meta["exchangeTimezoneName"],
            as_of=frame.timestamp.iloc[-1].to_pydatetime(), fetched_at=fetched_at,
            history=frame[[c for c in ("date", "close", "volume") if c in frame]],
            delay_minutes=delay if isinstance(delay, int) and delay >= 0 else None,
        )
    except MarketDataError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, AttributeError) as exc:
        raise MarketDataError(f"{symbol}：数据源响应格式异常。") from exc


class YahooMarketDataProvider:
    source_label = SOURCE

    def fetch(self, symbol: str) -> MarketSeries:
        symbol = normalize_symbol(symbol)
        try:
            response = requests.get(
                ENDPOINT + symbol,
                params={"range": "2y", "interval": "1d", "includePrePost": "false"},
                headers={"User-Agent": "GlobalMarketIntelligence/0.2 (research dashboard)"},
                timeout=(3.05, 8),
            )
            if response.status_code == 429:
                raise MarketDataError(f"{symbol}：数据源限流，请稍后重试。")
            response.raise_for_status()
            payload = response.json()
        except MarketDataError:
            raise
        except requests.RequestException as exc:
            raise MarketDataError(f"{symbol}：行情请求失败，请检查网络或稍后重试。") from exc
        except ValueError as exc:
            raise MarketDataError(f"{symbol}：数据源未返回有效 JSON。") from exc
        return parse_chart(symbol, payload, datetime.now(timezone.utc))

    def fetch_many(self, symbols: tuple[str, ...]) -> tuple[dict[str, MarketSeries], dict[str, str]]:
        if len(symbols) > 12:
            raise MarketDataError("每次最多查询 12 个资产。")

        def fetch_one(symbol):
            try:
                return symbol, self.fetch(symbol), None
            except MarketDataError as exc:
                return symbol, None, str(exc)

        results, errors = {}, {}
        with ThreadPoolExecutor(max_workers=4) as pool:
            for symbol, series, error in pool.map(fetch_one, dict.fromkeys(symbols)):
                if error:
                    errors[symbol] = error
                else:
                    results[symbol] = series
        return results, errors
