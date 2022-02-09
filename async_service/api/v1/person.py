from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from models.person import Person
from pydantic import BaseModel
from pydantic.validators import UUID
from services.person import PersonService, get_person_service

router = APIRouter()


class FilmList(BaseModel):
    id: UUID
    title: str
    imdb_rating: Optional[float]


@router.get("/search", response_model=List[Person])
async def person_search(
        query: str, person_service: PersonService = Depends(get_person_service),
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]")
) -> List[Person]:
    persons = await person_service.get_list(page_size=page_size, page_number=page_number, query=query)
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
async def film_list(
        film_service: PersonService = Depends(get_person_service),
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        person_id: Optional[UUID] = Query(None, alias="filter[genre]")
) -> List[Person]:
    films = await film_service.get_films_by_person(page_size=page_size, page_number=page_number, perosn_id=person_id)
    return films
