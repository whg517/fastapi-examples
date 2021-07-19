import asyncio

import pytest
from fastapi_with_sqlalchemy.db.models import User
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_with_sqlalchemy.db import Database, session_provider, SessionProvider


@pytest.mark.asyncio
async def test_database():
    async with Database() as d1:
        async with Database() as d2:
            assert d1 == d2
            assert d1.engine == d2.engine


@pytest.mark.asyncio
async def test_engine():
    async with Database() as db:
        async with db.engine.connect() as connector:
            def get_table_names(conn: Connection):
                inspector = inspect(conn)
                return inspector.get_table_names()

            table_names = await connector.run_sync(get_table_names)

            assert table_names
            assert 'alembic_version' in table_names


@pytest.mark.asyncio
async def test_session(migrate):
    async with Database() as db:
        async with db.session() as session:
            result = await session.scalar(text('SELECT * FROM alembic_version'))
            assert result


@pytest.mark.asyncio
async def test_session_provider_1(migrate, server):
    @session_provider()
    async def _func(session: AsyncSession):
        return await session.scalar(text('SELECT * FROM alembic_version'))

    assert await _func()

    @session_provider()
    async def _func(session: AsyncSession):
        return await session.scalar(text('SELECT * FROM alembic_version'))

    async with server.db.session() as se:
        assert await _func(se)

    @session_provider()
    async def _func():
        """"""

    with pytest.raises(ValueError):
        assert await _func()


@session_provider(auto_commit=True)
async def func(session: AsyncSession):
    user = User(name='foo', age=12)
    session.add(user)
    await session.commit()


@pytest.mark.asyncio
async def test_session_provider(migrate, server, session):
    await func()

    res = await session.scalar(text('SELECT COUNT(*) FROM user'))
    assert res
