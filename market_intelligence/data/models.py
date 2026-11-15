"""Small provider contract; future APIs should implement this interface."""

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


@dataclass(frozen=True)
class Asset:
    symbol: str
    name: str
    category: str
    reference_price: float
    daily_volatility: float
    currency: str = "USD"


class MarketDataProvider(Protocol):
    source_label: str

    def assets(self) -> tuple[Asset, ...]: ...

    def history(self, symbol: str) -> pd.DataFrame:
        """Return date and close columns, ascending by date."""
        ...

    def snapshot(self) -> pd.DataFrame:
        """Return quotes with symbol, name, category, currency, price, change_pct."""
        ...
