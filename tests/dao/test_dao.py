import inspect

import pytest

from fastapi_with_sqlalchemy.dao.base import UserDAO
from fastapi_with_sqlalchemy.db.models import User
from fastapi_with_sqlalchemy.utils.exceptions import ObjectNotFound
from sqlalchemy import select, func
from sqlalchemy.exc import InvalidRequestError


@pytest.fixture()
async def dao(server):
    async with server.db.session() as session:
        dao = UserDAO(session)
        yield dao


@pytest.mark.parametrize(
    'sort, search, expect_value',
    [
        (None, None, 'lt'),
        (['id'], None, 'lt',),
        (['-id'], None, 'gt'),
        (None, {'name': 'bar'}, 'gt'),
        (None, {'abc': 'bar'}, InvalidRequestError),
    ]
)
@pytest.mark.asyncio
async def test_get(
        init_user,
        session,
        dao,
        sort,
        search,
        expect_value
):
    """Test get multi object."""
    kwargs = {}
    if search:
        kwargs.setdefault('search_fields', search)
    if sort:
        kwargs.setdefault('sorting_fields', sort)
    if inspect.isclass(expect_value) and issubclass(expect_value, Exception):
        with pytest.raises(expect_value):
            await dao.get(**kwargs)
    else:
        objs = await dao.get(**kwargs)
        assert objs

        if len(objs) > 1:

            stmt = select(func.count()).select_from(User)
            assert len(objs) == await session.scalar(stmt)
            if expect_value == 'gt':
                assert objs[0].id > objs[1].id
            elif expect_value == 'lt':
                assert objs[0].id < objs[1].id
        else:
            k, v = search.popitem()
            obj = objs[0]
            assert getattr(obj, k) == v


@pytest.mark.parametrize(
    'pk, expect_value',
    [
        (1, None),
        (10, ObjectNotFound)
    ]
)
@pytest.mark.asyncio
async def test_get_by_id(
        init_user,
        session,
        dao,
        pk,
        expect_value,
):
    if expect_value:
        with pytest.raises(expect_value):
            await dao.get_by_id(pk)
    else:
        obj = await dao.get_by_id(pk)
        assert obj.id == pk


