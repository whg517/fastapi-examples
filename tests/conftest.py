"""Conf test"""
import functools
import os
from collections import AsyncGenerator, Generator, Callable
from datetime import datetime
from typing import Optional

import pytest
from alembic.command import downgrade as alembic_downgrade
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from requests import Response
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import Session, sessionmaker

from fastapi_with_sqlalchemy.config import settings as project_settings
from fastapi_with_sqlalchemy.db.models import User, Address
from fastapi_with_sqlalchemy.server import Server
from starlette.testclient import TestClient


@pytest.fixture()
def settings():
    """settings fixture"""
    return project_settings


@pytest.fixture()
def migrate(settings):
    """migrate fixture."""
    cwd = os.getcwd()
    os.chdir(os.path.join(settings.BASE_DIR, 'alembic'))
    alembic_config = AlembicConfig(settings.BASE_DIR / 'alembic' / 'alembic.ini')
    alembic_downgrade(alembic_config, 'base')
    alembic_upgrade(alembic_config, 'head')
    try:
        yield
    finally:
        alembic_downgrade(alembic_config, 'base')
        # try:
        #     os.remove(urlparse(settings.DATABASE).path)
        # except FileNotFoundError:
        #     pass
    os.chdir(cwd)


@pytest.fixture()
async def session_factory(settings):
    """Session factory fixture"""
    engine = create_async_engine(
        settings.DATABASE,
        echo=True,
    )
    yield sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=True,
        expire_on_commit=False,
    )

    await engine.dispose()


@pytest.fixture()
async def session(migrate, session_factory) -> AsyncSession:
    """Session fixture."""
    async with session_factory() as _session:
        yield _session


@pytest.fixture()
async def init_user(session):
    async with session.begin():
        users = [
            User(name='foo', age=12),
            User(name='bar', age=13)
        ]
        session.add_all(users)


@pytest.fixture()
async def init_address(init_user, session):
    async with session.begin():
        user = await session.scalar(select(User))
        addresses = [
            Address(user_id=user.id, city='bj', country='CN'),
            Address(user_id=user.id, city='sh', country='CN')
        ]
        session.add_all(addresses)


API_VERSION = 'v1'


@pytest.fixture()
def url_builder() -> Callable[[str], str]:
    def _builder(path: str):
        path = path.lstrip('/')
        return f'/api/{API_VERSION}/{path}'

    return _builder


@pytest.fixture()
def assert_status_code_factory() -> Callable[[Response, Optional[int]], None]:
    """Check state code is ok."""

    def _factory(response: Response, code: int = 200) -> None:
        """Check state code is ok."""
        assert response.status_code == code

    return _factory


@pytest.fixture(autouse=True)
async def server(migrate) -> Server:
    """Server fixture"""
    s = Server()
    try:
        await s.start()
        yield s
    finally:
        await s.stop()


@pytest.fixture()
async def api_client(server) -> TestClient:
    client = TestClient(server.rest_api.app)
    yield client
