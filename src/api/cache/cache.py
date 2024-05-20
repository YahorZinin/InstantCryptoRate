import asyncio
import typing as tp

import redis.asyncio as redis

from src.api.cache.utils import find_newest_pair, normalized_pair
from src.client.providers.base import BaseCurrencyPair


class Cache:
    _pool: redis.Redis

    def __init__(self):
        self.__pool = redis.BlockingConnectionPool(host="localhost", decode_responses=True)

    async def init(self) -> tp.Self:
        self._pool = await redis.Redis(connection_pool=self.__pool)
        return self

    def __await__(self):
        return self.init().__await__()

    async def close(self) -> None:
        await self.__pool.aclose()
        await self._pool.aclose()

    async def set_currency_pair(self, pair: BaseCurrencyPair) -> None:
        await self._pool.hset(normalized_pair(*pair.base_quote_currencies), mapping={pair.slug: pair.model_dump_json()})

    def _create_tasks(self, task: tp.Coroutine, pair: tuple[str, str], *args) -> list[tp.Coroutine]:
        return [task(normalized_pair(*pair), *args), task(normalized_pair(*pair[::-1]), *args)]

    async def find_all(self, pair: str) -> None | list[BaseCurrencyPair]:
        requests = self._create_tasks(self._pool.hgetall, pair)
        for finished_request in asyncio.as_completed(requests):
            if results := await finished_request:
                return [BaseCurrencyPair.model_validate_json(r) for r in results.values()]
        return None

    async def find_one(self, pair: str, exchange: str) -> None | BaseCurrencyPair:
        requests = self._create_tasks(self._pool.hget, pair, exchange)
        for finished_request in asyncio.as_completed(requests):
            if result := await finished_request:
                return BaseCurrencyPair.model_validate_json(result)
        return None

    async def get(self, pair: tuple[str, str], exchange: None | str) -> None | BaseCurrencyPair:
        if exchange is None:
            if pairs := await self.find_all(pair):
                return find_newest_pair(pairs)
        else:
            return await self.find_one(pair, exchange)
        return None
