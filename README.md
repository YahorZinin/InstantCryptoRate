# InstantCryptoRate

## Service for Instantly Obtaining Prices of Currency Pairs

### Disclaimer
This code is not considered complete for several reasons:
- Inadequate error handling for Redis and lack of network error handling.
- Missing support for processing indirect pairs in polynomial time.
- Code requires cleaning as some parts have mixed responsibilities.
- A Docker image for the web server would be beneficial.

## Table of Contents
- [Usage](#usage)
- [Launch Server](#launch-server)
- [Sources](#sources)

## Usage

### Endpoint
`POST /api/v1/convert`

### Request Body
```json
{
    "currency_from": "BTC",
    "currency_to": "ETH",
    "exchange": "binance",
    "amount": 1.5,
    "cache_max_seconds": 30
}
```

This request converts 1.5 BTC to ETH using the Binance exchange, with a maximum cache time of 30 seconds.

### Accepted Values

- **currency_from, currency_to**: Non-empty strings
- **exchange**: Either `null` or one of the following strings:
  - `"kucoin"`
  - `"binance"`
- **amount**: A `Decimal` value greater than or equal to 0
- **cache_max_seconds**: Either `null` or an integer greater than 0

### Notes
- Ensure `currency_from` and `currency_to` are valid and non-empty strings representing the desired cryptocurrencies.
- If `exchange` is specified, it must be either `"kucoin"` or `"binance"`. If not specified, set it to `null`.
- `amount` must be a `Decimal` value that is 0 or greater.
- `cache_max_seconds` should be an integer greater than 0, or `null` if fresh data is required.

## Launch Server
```shell
poetry install
make start-dependencies
make start-web-server
```

## Sources
- **aiohttp** - [Documentation](https://docs.aiohttp.org/en/stable/)
- **Python Concurrency with asyncio by Matthew Fowler** - [Book](https://www.manning.com/books/python-concurrency-with-asyncio)
- **redis-py** - [Asyncio Examples](https://redis-py.readthedocs.io/en/stable/examples/asyncio_examples.html)