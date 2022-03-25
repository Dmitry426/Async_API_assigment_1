from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from async_service.api.v1 import film, genre, person

from .core.config import EsSettings, ProjectSettings
from .db import elastic, redis
from .db.redis import get_redis

base_settings = ProjectSettings()
es_settings = EsSettings()

app = FastAPI(
    title=base_settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    FastAPICache.init(RedisBackend(get_redis()), prefix="fastapi-cache")

    elastic.es = AsyncElasticsearch(hosts=[f"{es_settings.host}:{es_settings.port}"])


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(film.router, prefix="/api/v1/film", tags=["film"])
app.include_router(person.router, prefix="/api/v1/person", tags=["person"])
app.include_router(genre.router, prefix="/api/v1/genre", tags=["genre"])
