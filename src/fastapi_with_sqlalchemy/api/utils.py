from collections import Callable, AsyncGenerator
from typing import Type, TypeVar

from fastapi_with_sqlalchemy.service.base import Service
from starlette.requests import Request

RT = TypeVar('RT', bound=Service)


def service_depend(service_kls: Type[RT]) -> Callable[[Request], AsyncGenerator[RT, None]]:
    async def get_service(request: Request):
        db = request.app.extra.get('db')
        async with db.scoped_session() as local_session:
            async with local_session.begin():
                yield service_kls(local_session)

    return get_service
