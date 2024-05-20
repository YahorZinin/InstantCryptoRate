from src.client.providers.base.models import BaseCurrencyPair


def normalized_pair(currency_from: str, currency_to: str) -> str:
    return f"{currency_from.upper()}-{currency_to.upper()}"


def find_newest_pair(pairs: list[BaseCurrencyPair]) -> BaseCurrencyPair:
    newest = pairs[0]
    for pair in pairs:
        if newest.fetched_at_timestamp < pair.fetched_at_timestamp:
            newest = pair
    return newest
