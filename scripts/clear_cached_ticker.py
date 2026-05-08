import argparse

from portfolio_builder.data.price_service import clear_cached_ticker


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", help="Ticker to remove from the local cache")
    args = parser.parse_args()

    deleted_rows = clear_cached_ticker(args.ticker)

    print(f"Deleted {deleted_rows} cached rows for {args.ticker.upper()}.")


if __name__ == "__main__":
    main()
