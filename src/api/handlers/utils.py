from decimal import Decimal
from http import HTTPStatus

from aiohttp import web
from pydantic import BaseModel

from src.api.models.convert import RequestModel, ResponseModel
from src.client.providers.base.models import BaseCurrencyPair
from src.utils import get_current_utc_timestamp


def rate_consider_request(request_from: str, pair: BaseCurrencyPair) -> Decimal:
    if request_from == pair.base_quote_currencies[0]:
        return pair.price
    return Decimal(1) / pair.price


def calculate_response(request: RequestModel, pair: BaseCurrencyPair) -> ResponseModel:
    rate = rate_consider_request(request.currency_from, pair)
    return ResponseModel(
        currency_from=request.currency_from,
        currency_to=request.currency_to,
        exchange=pair.slug,
        rate=rate,
        result=rate * request.amount,
        updated_at=pair.fetched_at_timestamp,
    )


def is_data_expired(limit: int, data_timestamp: int) -> bool:
    return (get_current_utc_timestamp() - data_timestamp) > limit


def generate_response_for_pair(
    request_model: RequestModel, pair: BaseCurrencyPair, status: int = HTTPStatus.OK
) -> web.Response:
    response_model = calculate_response(request_model, pair)
    return web.json_response(body=response_model.model_dump_json(), status=status)


class ErrorResponseTemplate(BaseModel):
    message: str
    status: int


def generate_error_response(message: str, status: int = HTTPStatus.BAD_REQUEST) -> web.Response:
    body = ErrorResponseTemplate(message=message, status=status)
    return web.json_response(body=body.model_dump_json(), status=status)
