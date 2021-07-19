from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_with_sqlalchemy.dao.base import DAO, UserDAO


class Service:
    DAO_KLS: Type[DAO]

    def __init__(self, session: AsyncSession):
        self.dao = self.DAO_KLS(session)

    async def get_by_id(self, pk):
        return await self.dao.get_by_id(pk)

    async def get(
            self,
    ):
        return await self.dao.get()


class UserService(Service):
    DAO_KLS = UserDAO
