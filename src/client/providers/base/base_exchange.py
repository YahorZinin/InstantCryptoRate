import asyncio
from abc import ABC, abstractmethod
from typing import Protocol

from aiohttp import ClientSession

from src.utils import get_current_utc_timestamp

from .models import BaseCurrencyPair, BaseExchangeConfig, BaseRawResponse


class SupportBool(Protocol):
    def __bool__(self) -> bool:
        ...


class BaseExchange(ABC):
    slug: str
    _config: BaseExchangeConfig
    _raw_response_model = BaseRawResponse

    def _generate_url(self, postfix: str) -> str:
        return self._config.base_url + self._config.api_version + postfix

    def _find_success_result(self, results: list[SupportBool]) -> SupportBool | None:
        return next((result for result in results if result), None)

    @staticmethod
    @abstractmethod
    def symbol_normalization(currency_from: str, currency_to: str) -> str:
        ...

    @staticmethod
    @abstractmethod
    def _serialize_successful_response(raw_response: BaseRawResponse) -> BaseCurrencyPair:
        ...

    async def find_rate(self, session: ClientSession, symbol: tuple[str, str]) -> BaseCurrencyPair | None:
        results = await asyncio.gather(
            self._fetch_rate(session, symbol),
            self._fetch_rate(session, symbol[::-1]),
        )
        if result := self._find_success_result(results):
            return self._serialize_successful_response(result)
        return None

    async def fetch_rate(self, session: ClientSession, symbol: tuple[str, str]) -> BaseCurrencyPair | None:
        if result := await self._fetch_rate(session, symbol):
            return self._serialize_successful_response(result)
        return None

    async def _fetch_rate(self, session: ClientSession, base_quote_currencies: tuple[str, str]) -> BaseRawResponse:
        async with session.get(
            self._generate_url(self._config.fetch_price_url),
            params={"symbol": self.symbol_normalization(*base_quote_currencies)},
        ) as response:
            return self._raw_response_model(
                status=response.status,
                body=await response.json(),
                fetched_at_timestamp=get_current_utc_timestamp(),
                base_quote_currencies=base_quote_currencies,
            )
