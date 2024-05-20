from decimal import Decimal

from pydantic import BaseModel


class BaseExchangeConfig(BaseModel):
    base_url: str
    api_version: str
    fetch_price_url: str


class BaseRawResponse(BaseModel):
    status: int
    base_quote_currencies: tuple[str, str]
    fetched_at_timestamp: int

    def __bool__(self) -> bool:
        ...


class BaseCurrencyPair(BaseModel):
    slug: str
    base_quote_currencies: tuple[str, str]
    fetched_at_timestamp: int
    price: Decimal
