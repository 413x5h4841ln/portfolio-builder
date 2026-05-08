from portfolio_builder.data.price_service import get_cache_summary


def main() -> None:
    summary = get_cache_summary()

    if summary.empty:
        print("No cached price data found.")
        return

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
