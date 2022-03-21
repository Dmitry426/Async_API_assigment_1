from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from pydantic.validators import UUID

from async_service.core.config import API_CACHE_TTL
from async_service.models.genre import Genre
from async_service.services.base_service import GenreService, get_genre_service

router = APIRouter()


@router.get(
    "/{genre_id}", response_model=Genre, name="Genre by ID",
    description="Returns specific genre by its UUID."
)
@cache(expire=API_CACHE_TTL)
async def genre_details(
        genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)
) -> BaseModel:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return genre


@router.get(
    "/", response_model=List[Genre], name="Genre list",
    description="Returns list with all genres in database"
)
@cache(expire=API_CACHE_TTL)
async def genre_list(genre_service: GenreService = Depends(get_genre_service)
                     , page_size: int = Query(50, alias="page[size]"),
                     page_number: int = Query(1, alias="page[number]")
                     ) -> List[Genre]:
    sort = {"name.raw": "asc"}
    genres = await genre_service.get_list_search(sort=sort, page_number=page_number,
                                                 page_size=page_size)
    return genres
