from db import elastic, redis
from core.logger import LOGGING
from core import config
from api.api_v1 import film
import logging

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"]
    )


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()

app.include_router(film.router, prefix="/api/api_v1/film", tags=["film"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.environ.get("UVICORN_HOST"),
        port=os.environ.get("UVICORN_PORT"),
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
