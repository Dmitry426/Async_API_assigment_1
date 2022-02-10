from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pydantic.validators import UUID
from services.person import PersonService, get_person_service

from .film import FilmList

router = APIRouter()


class Person(BaseModel):
    id: UUID
    full_name: str
    role: List[str]
    film_works: List[UUID]


@router.get("/search", response_model=List[Person])
async def person_search(
        query: str, person_service: PersonService = Depends(get_person_service),
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]")
) -> List[Person]:
    persons = await person_service.get_list(page_size=page_size, page_number=page_number, query=query)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The is no such person ")
    return persons


@router.get("/{person_id}", response_model=Person)
async def person_details(
        person_id: UUID, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The is no such person ")

    return person


@router.get("/{person_id}/film/", response_model=List[FilmList])
async def person_list(
        film_service: PersonService = Depends(get_person_service),
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        person_id: Optional[UUID] = Query(None, alias="filter[genre]")
) -> List[Person]:
    films = await film_service.get_films_by_person(page_size=page_size, page_number=page_number, person_id=person_id)
    return films
