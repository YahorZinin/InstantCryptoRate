import typing as tp
from http import HTTPStatus

from src.client.providers.base import BaseCurrencyPair, BaseExchange, BaseExchangeConfig, BaseRawResponse
from src.utils import get_current_utc_timestamp

BINANCE_SLUG = "binance"


class CurrencyPair(BaseCurrencyPair):
    slug: str = BINANCE_SLUG


class RawResponse(BaseRawResponse):
    body: dict[str, tp.Any] = {}

    def __bool__(self) -> bool:
        return self.status == HTTPStatus.OK and bool(self.body)


class BinanceConfig(BaseExchangeConfig):
    ...


class BinanceExchange(BaseExchange):
    slug: str = BINANCE_SLUG
    _config: BinanceConfig = BinanceConfig(
        base_url="https://api.binance.com/api", api_version="/v3", fetch_price_url="/ticker/price"
    )
    _raw_response_model = RawResponse

    @staticmethod
    def symbol_normalization(currency_from: str, currency_to: str) -> str:
        return f"{currency_from.upper()}{currency_to.upper()}"

    @staticmethod
    def _serialize_successful_response(raw_response: RawResponse) -> CurrencyPair:
        return CurrencyPair(
            price=raw_response.body.get("price"),
            base_quote_currencies=raw_response.base_quote_currencies,
            fetched_at_timestamp=get_current_utc_timestamp(),
        )
