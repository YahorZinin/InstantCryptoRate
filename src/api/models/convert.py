from decimal import Decimal

from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated

from src.client.providers.repository import exchanges


class RequestModel(BaseModel):
    currency_from: str
    currency_to: str
    exchange: str | None = None
    amount: Annotated[Decimal, Field(strict=True, ge=0)]
    cache_max_seconds: Annotated[int, Field(strict=True, gt=0)] | None = None

    @property
    def symbol(self) -> tuple[str, str]:
        return self.currency_from, self.currency_to

    @field_validator("exchange")
    @classmethod
    def exchanger_supported(cls, exchange: str | None) -> str | None:
        if isinstance(exchange, str):
            exchange = exchange.lower()
            found = exchanges.find_exchange_by_slug(exchange)
            if not found:
                raise ValueError("exchanger is not supported")
        return exchange

    @field_validator("currency_from", "currency_to")
    @classmethod
    def convert_to_uppercase(cls, value):
        if not isinstance(value, str):
            raise ValueError("must be a string")
        return value.upper()


class ResponseModel(BaseModel):
    currency_from: str
    currency_to: str
    exchange: str | None
    rate: Decimal
    result: Decimal
    updated_at: int
