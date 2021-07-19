import pytest
from sqlalchemy import select

from fastapi_with_sqlalchemy.db.models import User


@pytest.mark.asyncio
async def test_migrate(session):
    """
    Test migrate.
    :param session:
    :return:
    """
    async with session.bind.connect() as connection:
        tables_name = await connection.run_sync(session.bind.dialect.get_table_names)
        assert tables_name
        assert 'user' in tables_name


@pytest.mark.asyncio
async def test_db(init_user, session):
    obj = await session.scalar(select(User))
    assert obj
    assert isinstance(obj, User)
