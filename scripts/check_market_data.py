"""Explicit live check; run from repository root, not as part of offline CI."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_intelligence.data.yahoo import YahooMarketDataProvider  # noqa: E402


def main() -> int:
    results, errors = YahooMarketDataProvider().fetch_many(("AAPL", "SPY"))
    for symbol, item in results.items():
        print(f"{symbol}: {item.price:.2f} {item.currency}; bar={item.as_of.isoformat()}; "
              f"fetched={item.fetched_at.isoformat()}; rows={len(item.history)}")
    for error in errors.values():
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
