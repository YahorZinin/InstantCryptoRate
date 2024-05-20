import asyncio
import typing as tp

import aiohttp

from src.client.providers.base.base_exchange import BaseExchange
from src.client.providers.repository import ExchangesRepository

exchanges = ExchangesRepository()


def select_an_exchangers(exchange: str | None) -> list[BaseExchange]:
    if exchange is not None:
        return [exchanges.find_exchange_by_slug(exchange)]
    return exchanges.exchanges


# async def exchange_scraper(
#     session, exchange_slug: str, known_pair_order: bool, symbol: tuple[str, str]
# ):  # -> Any | None:
#     exchanges = select_an_exchangers(exchange_slug)
#     if known_pair_order:
#         exchanges_requests = [asyncio.create_task(exch.fetch_rate(session, symbol)) for exch in exchanges]
#     else:
#         exchanges_requests = [asyncio.create_task(exch.find_rate(session, symbol)) for exch in exchanges]
#     done, pending = await asyncio.wait(exchanges_requests, return_when=asyncio.FIRST_COMPLETED, timeout=1)
#     for done_task in done:
#         result = await done_task
#         if result is not None:
#             [pd.cancel() for pd in pending]
#             return result
#     return None


class ExchangeScraper:
    _session: aiohttp.ClientSession
    _exchanges: list[BaseExchange]

    def __init__(self, session: aiohttp.ClientSession, exchange_slug: str) -> None:
        self._session = session
        self._exchanges = select_an_exchangers(exchange_slug)

    def _cancel_pending_tasks(self, pending) -> None:
        for p in pending:
            p.cancel()

    async def _exchanges_task_runner(self, requests: list[tp.Coroutine]):
        done, pending = await asyncio.wait(requests, return_when=asyncio.FIRST_COMPLETED, timeout=1)
        for done_task in done:
            result = await done_task
            if result := await done_task:
                self._cancel_pending_tasks(pending)
                return result
        return None

    async def fetch_reliable_currency_pair(self, symbol: tuple[str, str]):
        requests = [asyncio.create_task(exch.fetch_rate(self._session, symbol)) for exch in self._exchanges]
        return await self._exchanges_task_runner(requests)

    async def find_currency_pair(self, symbol: tuple[str, str]):
        requests = [asyncio.create_task(exch.find_rate(self._session, symbol)) for exch in self._exchanges]
        return await self._exchanges_task_runner(requests)
