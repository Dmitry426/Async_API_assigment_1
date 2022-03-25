from abc import ABC
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from async_service.core.config import JwtSettings
from async_service.db.elastic import get_elastic
from async_service.models.film import Film
from async_service.models.genre import Genre
from async_service.models.person import Person
from async_service.services.es_service import EsService
from async_service.services.jwt_utils import Auth

jwt = JwtSettings()


class FilmService(EsService, ABC):
    elastic_index_name = "movies"
    response_model = Film


@lru_cache
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)


class GenreService(EsService, ABC):
    elastic_index_name = "genres"
    response_model = Genre


@lru_cache
def get_genre_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)


class PersonService(EsService, ABC):
    elastic_index_name = "persons"
    response_model = Person


@lru_cache
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)


class AuthService(Auth, ABC):
    secret_key = jwt.secret_key
    algorithm = jwt.algorithm
