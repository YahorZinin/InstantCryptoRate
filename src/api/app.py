import asyncio

import aiohttp
from aiohttp import web
from aiojobs.aiohttp import setup

from src.api.cache.cache import Cache
from src.api.handlers.convert import convert_handler
from src.api.utils import CACHE_KEY, CLIENT_SESSION_KEY


async def create_redis_connection(application: web.Application) -> None:
    application[CACHE_KEY] = await Cache()


async def create_client_session(application: web.Application) -> None:
    application[CLIENT_SESSION_KEY] = aiohttp.ClientSession()


async def close_client_session(application: web.Application) -> None:
    await application[CLIENT_SESSION_KEY].close()
    # sleep to allow underlying connections to close
    await asyncio.sleep(0)


async def close_redis_pool(application: web.Application) -> None:
    await application[CACHE_KEY].close()


app = web.Application()
app.router.add_post("/api/v1/convert", convert_handler)

app.on_startup.append(create_redis_connection)
app.on_startup.append(create_client_session)

app.on_cleanup.append(close_client_session)
app.on_cleanup.append(close_redis_pool)
setup(app)
web.run_app(app)
