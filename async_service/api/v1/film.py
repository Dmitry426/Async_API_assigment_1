from http import HTTPStatus
from typing import List, Optional


from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache

from pydantic import BaseModel
from pydantic.validators import UUID

from async_service.core.config import API_CACHE_TTL
from async_service.models.film import PersonGenreFilm
from async_service.models.genre import Genre
from async_service.services.base_service import get_film_service, FilmService

router = APIRouter()


class FilmList(BaseModel):
    id: UUID
    title: str
    rating: float = None


class FilmDetail(FilmList):
    description: Optional[str]
    genres: Optional[List[Genre]]
    actors: Optional[List[PersonGenreFilm]]
    writers: Optional[List[PersonGenreFilm]]
    directors: Optional[List[PersonGenreFilm]]


@router.get(
    "/search", response_model=List[FilmList], name="Films search",
    description="""
    Search through film titles by some arbitrary query.
    Returns paginated list of films sorted by search score.
    """
)
@cache(expire=API_CACHE_TTL)
async def film_search(
        query: str, film_service: FilmService = Depends(get_film_service),
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]")
) -> List[FilmList]:
    films = await film_service.get_list_search(page_size=page_size, page_number=page_number, query=query)
    return [FilmList(**film.dict(include={"id", "title", "imdb_rating"})) for film in films]


@router.get(
    "/{film_id}", response_model=FilmDetail, name="Film by ID",
    description="Returns specific film by its UUID."
)
@cache(expire=API_CACHE_TTL)
async def film_details(
        film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return FilmDetail(**film.dict(exclude={"actors_names", "writers_names"}))


@router.get(
    "/", response_model=List[FilmList], name="Films list",
    description="Returns paginated list of films sorted and filtered by corresponding params."
)
@cache(expire=API_CACHE_TTL)
async def film_list(
        film_service: FilmService = Depends(get_film_service),
        sort: str = Query("rating"), page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        filter_genre: Optional[UUID] = Query(None, alias="filter[genre]")
) -> List[FilmList]:
    films = await film_service.get_list_filter_by_id(page_size=page_size, page_number=page_number, sort=sort,
                                                     genre_id=filter_genre
                                                     )

    return [FilmList(**film.dict(include={"id", "title", "rating"})) for film in films]
