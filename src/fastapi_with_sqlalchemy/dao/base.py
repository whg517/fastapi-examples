from typing import Generic, Type, Union, Optional

from sqlalchemy import select, func
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
        return self._session

    async def count(self) -> int:
        """Get Model count"""
        stmt = select(func.count()).select_from(self.model)
        return await self.session.scalar(stmt)

    async def get_by_id(self, pk: int) -> ModelType:
        """Get model by id"""
        return await self.session.get(self.model, pk)

    def _select_stmt(self) -> Select:
        return select(self.model)

    async def get(
            self,
            sorting_fields: Optional[Union[set[str], list[str]]] = None,
            search_fields: Optional[dict[str, str]] = None,
            limit: int = 5,
            offset: int = 0,
    ):
        """
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
        filter_by_condition = {}
        for key, value in search_fields.items():
            table_field = getattr(self.model, key)
            filter_by_condition.setdefault(table_field, value)
        return stmt.filter_by(**filter_by_condition)

    def _paginate_by_limit_offset(self, stmt: Select, limit: int, offset: int) -> Select:
        """Page"""
        return stmt.limit(limit).offset(offset)


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
