import typing as tp
from http import HTTPStatus

from src.client.providers.base import BaseCurrencyPair, BaseExchange, BaseExchangeConfig, BaseRawResponse
from src.utils import get_current_utc_timestamp

KU_COIN_SLUG = "kucoin"


class CurrencyPair(BaseCurrencyPair):
    slug: str = KU_COIN_SLUG


class RawResponse(BaseRawResponse):
    body: dict[str, tp.Any] | None = None

    def __bool__(self) -> bool:
        def status_ok() -> bool:
            return self.status == HTTPStatus.OK

        def body_ok() -> bool:
            return self.body is not None and self.body.get("data") is not None

        return status_ok() and body_ok()


class KuCoinConfig(BaseExchangeConfig):
    ...


class KuCoinExchange(BaseExchange):
    slug: str = KU_COIN_SLUG
    _config: KuCoinConfig = KuCoinConfig(
        base_url="https://api.kucoin.com/api", api_version="/v1", fetch_price_url="/market/orderbook/level1"
    )
    _raw_response_model = RawResponse

    @staticmethod
    def symbol_normalization(currency_from: str, currency_to: str) -> str:
        return f"{currency_from.upper()}-{currency_to.upper()}"

    @staticmethod
    def _serialize_successful_response(raw_response: RawResponse) -> CurrencyPair:
        data = raw_response.body.get("data")
        return CurrencyPair(
            price=data.get("price"),
            base_quote_currencies=raw_response.base_quote_currencies,
            fetched_at_timestamp=get_current_utc_timestamp(),
        )
