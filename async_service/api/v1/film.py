from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import GenreFilmWork, PersonFilmWork
from pydantic import BaseModel
from pydantic.validators import UUID
from services.film import FilmService, get_film_service

router = APIRouter()


class FilmList(BaseModel):
    id: UUID
    title: str
    imdb_rating: Optional[float]


class FilmDetail(FilmList):
    description: Optional[str]
    genres: Optional[List[GenreFilmWork]]
    actors: Optional[List[PersonFilmWork]]
    writers: Optional[List[PersonFilmWork]]
    directors: Optional[List[PersonFilmWork]]


@router.get("/search", response_model=List[FilmList])
async def film_search(
    query: str, film_service: FilmService = Depends(get_film_service), page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]")
) -> List[FilmList]:
    films = await film_service.get_list(page_size=page_size, page_number=page_number, query=query)
    return films


@router.get("/{film_id}", response_model=FilmDetail)
async def film_details(
    film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return film


@router.get("/", response_model=List[FilmList])
async def film_list(
        film_service: FilmService = Depends(get_film_service),
        sort: str = Query("-imdb_rating"), page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        filter_genre: Optional[UUID] = Query(None, alias="filter[genre]")
        ) -> List[FilmList]:
    films = await film_service.get_list(page_size=page_size, page_number=page_number, sort=sort, genre_id=filter_genre)
    return films
