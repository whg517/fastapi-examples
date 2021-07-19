import pytest

from fastapi_with_sqlalchemy.dao.base import UserDAO


@pytest.fixture()
async def dao(server):
    async with server.db.session() as session:
        dao = UserDAO(session)
        yield dao


@pytest.mark.asyncio
async def test_get(init_user, dao):
    obj = await dao.get_by_id(1)
    assert obj
    assert isinstance(obj, dao.model)
