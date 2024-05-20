from aiohttp import web
from aiohttp.web_request import Request
from pydantic import BaseModel, ValidationError


async def serialize_request(request: Request, model: BaseModel) -> BaseModel:
    if not request.can_read_body:
        raise web.HTTPBadRequest(reason="Can't read body")
    try:
        return model.model_validate_json(await request.text())
    except ValidationError as error:
        raise web.HTTPBadRequest(body=error.json(), content_type="application/json")
