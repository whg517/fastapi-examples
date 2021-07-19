from fastapi import APIRouter, Depends
from fastapi_with_sqlalchemy.service.base import UserService
from starlette.requests import Request


async def get_service(request: Request):
    db = request.app.extra.get('db')
    async with db.scoped_session() as local_session:
        yield UserService(local_session)


router = APIRouter(dependencies=[Depends(get_service)])


async def commons_params(length: int = 1):
    yield {'length': length}


# @router.get('/')
# async def get_multi(
#         service: UserService = Depends(get_service)
# ):
#     return await service.get()


@router.get('/{pk}')
async def get_user(
        pk: int,
        service: get_service = Depends()
):
    return await service.get_by_id(pk)
