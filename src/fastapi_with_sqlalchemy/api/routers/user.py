from fastapi import APIRouter, Depends
from fastapi_with_sqlalchemy.api.utils import service_depend
from fastapi_with_sqlalchemy.service.base import UserService, Service

router = APIRouter()


async def commons_params(length: int = 1):
    yield {'length': length}


@router.get('/users')
async def get(
        service: service_depend(UserService) = Depends()
):
    """
    Get users
    :param service:
    :return:
    """
    return await service.get()


@router.get('/users/{pk}')
async def get_get_by_id(
        pk: int,
        service: service_depend(UserService) = Depends()
):
    """
    Get user by id
    :param pk:
    :param service:
    :return:
    """
    return await service.get_by_id(pk)


@router.post('/users')
async def create(
        name: str,
        age: int,
        service: service_depend(UserService) = Depends(),
):
    """
    Create a user
    :param name: 
    :param age: 
    :param service: 
    :return: 
    """

    await service.create()