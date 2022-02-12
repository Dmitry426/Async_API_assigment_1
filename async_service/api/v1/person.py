from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from models.person import Person
from pydantic.validators import UUID
from services.person import PersonService, get_person_service

from .film import FilmList

router = APIRouter()


@router.get(
    "/search", response_model=List[Person], name="Search person",
    description="""
    Search through person full name or role by some arbitrary query.
    Returns paginated list of persons sorted by search score.
    """
    )
async def person_search(
        query: str, person_service: PersonService = Depends(get_person_service),
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]")
) -> List[Person]:
    persons = await person_service.get_list(page_size=page_size, page_number=page_number, query=query)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The is no such person ")
    return persons


@router.get(
    "/{person_id}", response_model=Person, name="Person by ID",
    description="Returns specific person by its UUID."
    )
async def person_details(
        person_id: UUID, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The is no such person ")

    return person


@router.get(
    "/{person_id}/film/", response_model=List[FilmList], name="Get films by person ID",
    description="Returns list films in which person took any part."
    )
async def person_list(
        person_id: UUID,
        film_service: PersonService = Depends(get_person_service),
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
) -> List[Person]:
    films = await film_service.get_films_by_person(page_size=page_size, page_number=page_number, person_id=person_id)
    return [FilmList(id=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]
