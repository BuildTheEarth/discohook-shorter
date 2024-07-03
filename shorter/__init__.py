import asyncio
import os

from redis import asyncio as aioredis
from quart import Quart, exceptions
from quart_cors import cors

import shorter.bp.shortener
from shorter import config
from shorter.errors import ApiError
app = Quart(__name__)
app = cors(app, expose_headers=["Location"])


app.register_blueprint(shorter.bp.shortener.bp)


@app.before_serving
async def before_serving():

    cpool = aioredis.ConnectionPool.from_url(
        config.redis_address,
        encoding="utf-8",
    )

    app.redis = aioredis.Redis.from_pool(cpool)


@app.errorhandler(ApiError)
def handle_api_error(error: ApiError):
    return {
        "message": error.message,
        **error.payload,
    }, error.status_code


@app.errorhandler(exceptions.HTTPException)
def handle_exception(exception: exceptions.HTTPException):
    try:
        return {"message": exception.name}, exception.status_code
    except AttributeError:
        return {"message": "Internal Server Error"}, 500
