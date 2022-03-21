from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from pydantic.validators import UUID

from async_service.core.config import API_CACHE_TTL
from async_service.models.person import Person
from async_service.services.base_service import (
    FilmService,
    PersonService,
    get_film_service,
    get_person_service,
)

from .film import FilmList

router = APIRouter()


@router.get(
    "/search",
    response_model=List[Person],
    name="Search person",
    description="""
    Search through person full name or role by some arbitrary query.
    Returns paginated list of persons sorted by search score.
    """,
)
@cache(expire=API_CACHE_TTL)
async def person_search(
    query: str,
    person_service: PersonService = Depends(get_person_service),
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
) -> List[BaseModel]:
    persons = await person_service.get_list_search(
        page_size=page_size, page_number=page_number, query=query
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="The is no such person "
        )
    return persons


@router.get(
    "/{person_id}",
    response_model=Person,
    name="Person by ID",
    description="Returns specific person by its UUID.",
)
@cache(expire=API_CACHE_TTL)
async def person_details(
    person_id: UUID, person_service: PersonService = Depends(get_person_service)
) -> BaseModel:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="The is no such person "
        )

    return person


@router.get(
    "/{person_id}/film/",
    response_model=List[FilmList],
    name="Get films by person ID",
    description="Returns list films in which person took any part.",
)
@cache(expire=API_CACHE_TTL)
async def person_list(
    person_id: UUID,
    film_service: FilmService = Depends(get_film_service),
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
) -> List[FilmList]:
    films = await film_service.get_list_filter_by_id(
        page_size=page_size, page_number=page_number, person_id=person_id
    )
    return [
        FilmList(**film.dict(include={"id", "title", "imdb_rating"})) for film in films
    ]
