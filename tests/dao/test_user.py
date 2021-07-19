import pytest
from fastapi_with_sqlalchemy.dao.base import UserDAO
from fastapi_with_sqlalchemy.db.models import User


@pytest.fixture()
async def dao(server):
    async with server.db.session() as session:
        dao = UserDAO(session)
        yield dao


@pytest.mark.asyncio
async def test_get_user_by_address(init_address, dao):
    res = await dao.get_user_by_address(1)
    assert isinstance(res, User)
