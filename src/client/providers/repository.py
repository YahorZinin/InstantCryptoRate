from .base import BaseExchange
from .binance import BinanceExchange
from .ku_coin import KuCoinExchange


class ExchangesRepository:
    registered_exchanges = {
        BinanceExchange.slug: BinanceExchange(),
        KuCoinExchange.slug: KuCoinExchange(),
    }

    def find_exchange_by_slug(self, slug: str) -> BaseExchange | None:
        return self.registered_exchanges.get(slug)

    @property
    def exchanges(self) -> list[BaseExchange]:
        return list(self.registered_exchanges.values())

    @property
    def slugs(self) -> list[str]:
        return list(self.registered_exchanges.keys())


exchanges = ExchangesRepository()
