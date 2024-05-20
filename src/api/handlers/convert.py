import typing as tp

import aiohttp
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiojobs.aiohttp import spawn

from src.api.cache.cache import Cache
from src.api.handlers.utils import generate_error_response, generate_response_for_pair, is_data_expired
from src.api.models.convert import RequestModel
from src.api.serializer import serialize_request
from src.api.utils import CACHE_KEY, CLIENT_SESSION_KEY
from src.client.app import ExchangeScraper


async def client_error_handler(client_task: tp.Coroutine):
    try:
        return await client_task
    except aiohttp.ClientConnectorError as exc:
        raise web.HTTPServiceUnavailable(
            body="Currency pair providers are unable to process our request", content_type="application/json"
        ) from exc


async def make_requests_to_exchangers(scraper: ExchangeScraper, symbol: tuple[str, str], symbol_reliable: bool):
    search_method = scraper.find_currency_pair
    if symbol_reliable:
        search_method = scraper.fetch_reliable_currency_pair
    return await client_error_handler(search_method(symbol))


async def convert_handler(request: Request) -> Response:
    request_model = await serialize_request(request, RequestModel)
    cache: Cache = request.app[CACHE_KEY]
    symbol, is_reliable_symbol = request_model.symbol, False
    if request_model.cache_max_seconds:
        if pair := await cache.get(symbol, request_model.exchange):
            if not is_data_expired(limit=request_model.cache_max_seconds, data_timestamp=pair.fetched_at_timestamp):
                return generate_response_for_pair(request_model, pair)
            symbol, is_reliable_symbol = pair.base_quote_currencies, True

    exchange_scrapper = ExchangeScraper(request.app[CLIENT_SESSION_KEY], request_model.exchange)
    if pair := await make_requests_to_exchangers(exchange_scrapper, symbol, is_reliable_symbol):
        await spawn(request, cache.set_currency_pair(pair))
        return generate_response_for_pair(request_model, pair)

    # make search for indirect currency

    return generate_error_response(
        message="It seems we couldn't find the requested currency pair, please make sure the symbols are correct"
    )
