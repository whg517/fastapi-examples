from typing import Generic, Type, Union, Optional

from fastapi_with_sqlalchemy.utils.exceptions import ObjectNotFound
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_with_sqlalchemy.db.models import User, Address
from fastapi_with_sqlalchemy.utils.types import ModelType
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select


class DefaultFilter:
    """"""


class DefaultPaginator:
    """"""


class DAO(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """Async session"""
        return self._session

    async def count(self) -> int:
        """Get Model count"""
        stmt = select(func.count()).select_from(self.model)
        return await self.session.scalar(stmt)

    async def get_by_id(self, pk: int) -> ModelType:
        """
        Get model by id
        :param pk:
        :return: ModelType
        :raise ObjectNotFound
        """
        obj = await self.session.get(self.model, pk)
        if not obj:
            raise ObjectNotFound()
        return obj

    async def get(
            self,
            sorting_fields: Optional[Union[set[str], list[str]]] = None,
            search_fields: Optional[dict[str, str]] = None,
            limit: int = 5,
            offset: int = 0,
    ):
        """
        Get objects by conditions
        :return:
        """
        stmt = select(self.model)
        if sorting_fields:
            stmt = self._sort(stmt, sorting_fields)
        if search_fields:
            stmt = self._search(stmt, search_fields)
        stmt = self._paginate_by_limit_offset(stmt, limit, offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    def _sort(self, stmt: Select, sorting_fields: Union[tuple[str], list[str]]) -> Select:
        """Sort objects"""
        order_by_fields = []
        for field in sorting_fields:
            if field.startswith('-'):
                field = field[1:]
                table_field = getattr(self.model, field)
                order_by_fields.append(table_field.desc())
            else:
                table_field = getattr(self.model, field)
                order_by_fields.append(table_field.asc())
        return stmt.order_by(*order_by_fields)

    def _search(self, stmt: Select, search_fields: dict[str, str]) -> Select:
        """Search objects by some fields"""
        return stmt.filter_by(**search_fields)

    def _paginate_by_limit_offset(self, stmt: Select, limit: int, offset: int) -> Select:
        """Page"""
        return stmt.limit(limit).offset(offset)

    async def create(self, **kwargs) -> ModelType:
        """Create a model object"""
        model = self.model(**kwargs)
        self.session.add_all(model)
        return model

    async def update(self, pk: int, **kwargs) -> ModelType:
        obj = await self.get_by_id(pk)
        stmt = update(self.model).where(self.model.id == obj.id).values(**kwargs)
        obj = await self.session.scalar(stmt)
        return obj

    async def delete(self, pk: int) -> None:
        obj = await self.get_by_id(pk)
        stmt = delete(self.model).where(self.model.id == obj.id)
        await self.session.scalar(stmt)


class UserDAO(DAO[User]):
    model = User

    async def get_user_by_address(self, address_pk: int):
        """
        SalAlchemy 的动态加载机制无法在 Asyncio 中使用。
        即在一般情况下查询子表 Address 后，可以通过
        address.user 动态加载出父表的记录。或者在查询
        父表 User 后，通过 user.addresses 可以动态
        加载出子表的所有记录。
        但在 Asyncio 技术中，由于实现方法不同。是无法使用这种机制的。
        所以需要使用 `selectinload` 指定预加载的内容。

        更详细内容请阅读：
            https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
        :param address_pk:
        :return:
        """
        stmt = select(Address).filter(Address.id == address_pk).options(selectinload(Address.user))
        address = await self.session.scalar(stmt)
        return address.user


class AddressDAO(DAO[Address]):
    model = Address
