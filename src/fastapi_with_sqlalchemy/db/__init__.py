import functools
from collections import Awaitable, Callable
from inspect import signature
from typing import Optional, TypeVar, Any

from dynaconf import Dynaconf
from fastapi_with_sqlalchemy.utils import SingletonMeta
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import scoped_session, sessionmaker

from fastapi_with_sqlalchemy.utils.exceptions import FastAPIWithSqlalchemyError


class Database(metaclass=SingletonMeta):
    """
    example:
        db = Database()
        db.init(settings)
    """

    _engine: Optional[AsyncEngine] = None
    _settings: Optional[Dynaconf] = None

    def init(self, settings: Dynaconf) -> None:
        self._settings = settings

    @property
    def settings(self) -> Dynaconf:
        if self._settings is None:
            raise FastAPIWithSqlalchemyError('You should init Database.')
        return self._settings

    @property
    def engine(self) -> AsyncEngine:
        if not self._engine:
            self._engine = create_async_engine(self.settings.DATABASE)
        return self._engine

    @property
    def session(self) -> sessionmaker:
        return sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    def foo(self):
        """"""

    @property
    def scoped_session(self) -> scoped_session:
        return scoped_session(self.session)

    async def close(self) -> None:
        await self.engine.dispose()

    async def __aenter__(self) -> 'Database':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


def init_db(settings: Dynaconf) -> Database:
    db = Database()
    db.init(settings)
    return db


RT = TypeVar("RT")


def find_session_idx(func: Callable[..., Awaitable[RT]]) -> int:
    func_params = signature(func).parameters
    try:
        session_args_idx = tuple(func_params).index("session")
    except ValueError:
        raise ValueError(f"Function {func.__qualname__} has no `session` argument") from None

    return session_args_idx


class SessionProvider:
    """"""

    def __init__(self, auto_commit: Optional[bool] = False):
        self._auto_commit = auto_commit

    async def __aenter__(self) -> AsyncSession:
        async with Database().scoped_session() as session:
            self._session = session
            # 如果手动弃用自动提交，同时 session 没有开启事务
            if self._auto_commit and not session.in_transaction():
                async with session.begin():
                    return session
            else:
                return session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """"""

    def __call__(self, func: Callable[..., Awaitable[RT]]) -> Callable[..., Awaitable[RT]]:
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            session_args_idx = find_session_idx(func)
            # 方法已经以字典参数传递 session 。
            if "session" in kwargs or session_args_idx < len(args):
                result = await func(*args, **kwargs)
            else:
                async with self as session:
                    result = await func(*args, session=session, **kwargs)
            return result

        return inner


def session_provider(
        func: Optional[Callable[..., Awaitable[RT]]] = None,
        auto_commit: Optional[bool] = False
) -> RT:
    """
    Usage:
        >>>
            @session_provider()
            async def func(session: AsyncSession):
                result = await session.scalar(text('SELECT * from user'))
        >>>
            @session_provider(auto_commit=True)
            async def func(session: AsyncSession):
                result = await session.scalar(text('INSERT INTO user (name, age) VALUES ("foo", 123)'))
        >>>
            async def func(session: AsyncSession):
                result = await session.scalar(text('SELECT * from user'))
            result = await session_provider(func, auto_commit=True)

    :param func:
    :param auto_commit:
    :return:
    """
    if callable(func):
        return SessionProvider(auto_commit)(func)
    else:
        return SessionProvider(auto_commit)
