from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_cache.decorator import cache

from async_service.core.config import JwtSettings, RedisSettings
from async_service.serializers.auth import TokenData
from async_service.serializers.film import FilmDetail, FilmList
from async_service.services.base_service import (
    AuthService,
    FilmService,
    get_film_service,
)

router = APIRouter()
redis_settings = RedisSettings()
jwt = JwtSettings()

security = HTTPBearer(auto_error=False)
auth = AuthService()


@router.get(
    "/search",
    response_model=List[FilmList],
    name="Films search",
    description="""
    Search through film titles by some arbitrary query.
    Returns paginated list of films sorted by search score.
    """,
)
@cache(expire=redis_settings.cache_ttl)
async def film_search(
    query: str,
    film_service: FilmService = Depends(get_film_service),
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
    sort: str = Query("rating"),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> List[FilmList]:
    token = credentials
    roles: Optional[TokenData] = None
    if token:
        result = auth.decode_token(token=token.credentials)
        roles = TokenData(roles=result["roles"])
    if not token:
        roles = TokenData(roles=["visitor"])

    films = await film_service.get_list_search(
        page_size=page_size,
        page_number=page_number,
        query=query,
        sort=sort,
        roles=roles,
    )
    return [FilmList(**film.dict(include={"id", "title", "rating"})) for film in films]


@router.get(
    "/{film_id}",
    response_model=FilmDetail,
    name="Film by ID",
    description="Returns specific film by its UUID.",
)
@cache(expire=redis_settings.cache_ttl)
async def film_details(
    film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return FilmDetail(**film.dict(exclude={"actors_names", "writers_names", "role"}))


@router.get(
    "/",
    response_model=List[FilmList],
    name="Films list",
    description="""Returns paginated list of films sorted and filtered by
    corresponding params.""",
)
@cache(expire=redis_settings.cache_ttl)
async def film_list(
    film_service: FilmService = Depends(get_film_service),
    sort: str = Query("rating"),
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
    filter_genre: Optional[UUID] = Query(None, alias="filter[genre]"),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> List[FilmList]:
    token = credentials
    roles: Optional[TokenData] = None
    if token:
        result = auth.decode_token(token=token.credentials)
        roles = TokenData(roles=result["roles"])
    if not token:
        roles = TokenData(roles=["visitor"])

    films = await film_service.get_list_filter_by_id(
        page_size=page_size,
        page_number=page_number,
        sort=sort,
        genre_id=filter_genre,
        roles=roles,
    )

    return [FilmList(**film.dict(include={"id", "title", "rating"})) for film in films]
