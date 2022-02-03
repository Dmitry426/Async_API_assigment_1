from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pydantic.validators import UUID
from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: Optional[float]


@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:

        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return Film(id=film.id, title=film.title, imdb_rating=film.imdb_rating)


@router.get("/", response_model=Film)
async def film_list(
        film_service: FilmService = Depends(get_film_service),
        sort: str = Query("-imdb_rating"), page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        filter_genre: Optional[UUID] = Query(None, alias="filter[genre]")
        ) -> List[Film]:
    films = await film_service.get_list(sort, page_size, page_number, filter_genre)
    return films


@router.get("/search", response_model=Film)
async def film_search(
    query: str, film_service: FilmService = Depends(get_film_service), page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]")
):
    films = await film_service.get_list(page_size=page_size, page_number=page_number, query=query)
    return films
