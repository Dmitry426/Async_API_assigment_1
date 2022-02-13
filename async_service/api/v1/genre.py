from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic.validators import UUID

from models.genre import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get(
    "/{genre_id}", response_model=Genre, name="Genre by ID",
    description="Returns specific genre by its UUID."
    )
async def genre_details(
        genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return genre


@router.get(
    "/", response_model=List[Genre], name="Genre list",
    description="Returns list with all genres in database"
    )
async def genre_list(genre_service: GenreService = Depends(get_genre_service)) -> List[Genre]:
    genres = await genre_service.get_list()
    return genres
