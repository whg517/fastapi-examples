import functools
from asyncio import current_task
from collections import Awaitable, Callable
from inspect import signature
from typing import Optional, TypeVar, Any

from dynaconf import Dynaconf
from fastapi_with_sqlalchemy.utils import SingletonMeta
from sqlalchemy import event
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine, async_scoped_session, AsyncSessionTransaction)
from sqlalchemy.orm import sessionmaker

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

    @property
    def scoped_session(self) -> async_scoped_session:
        return async_scoped_session(self.session, scopefunc=current_task)

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
    """
    ?????? sqlalchemy.ext.async.session._AsyncSessionContextManager ??????
    ????????????????????? SessionProvider.
    """

    def __init__(self, auto_commit: Optional[bool] = False, nested: Optional[bool] = False):
        """
        SessionProvider
        :param auto_commit: ?????????????????????????????????
        :param nested:  ?????????????????????
        """
        self._auto_commit = auto_commit
        self._nested = nested
        self._session: Optional[AsyncSession] = None
        self._tarns: Optional[AsyncSessionTransaction] = None

    def _create_cm(self):
        """Return context manager"""
        return self

    async def __aenter__(self) -> AsyncSession:
        """
        ?????? _AsyncSessionContextManager.__enter__
        :return:
        """
        self._session: AsyncSession = Database().scoped_session()
        if self._auto_commit or self._nested:
            # ?????????????????????????????? async_session.begin()
            # AsyncSession ????????? begin ??? nested_begin ?????????
            # ???????????????????????????????????? nested ????????? True ???
            # AsyncSessionTransaction ?????????
            # ???????????????????????????????????????????????????????????? AsyncSession
            # ??????????????????
            self._trans = AsyncSessionTransaction(self._session, nested=self._nested)
            await self._trans.__aenter__()

        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        ?????? ?????? _AsyncSessionContextManager.__aexit__
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        if self._auto_commit:
            await self._trans.__aexit__(exc_type, exc_val, exc_tb)
        await self._session.__aexit__(exc_type, exc_val, exc_tb)

    def __call__(self, func: Callable[..., Awaitable[RT]]) -> Callable[..., Awaitable[RT]]:
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            session_args_idx = find_session_idx(func)
            # ????????????????????????????????? session ???
            if "session" in kwargs or session_args_idx < len(args):
                result = await func(*args, **kwargs)
            else:
                async with self._create_cm() as session:
                    result = await func(*args, session=session, **kwargs)
            return result

        return inner


def session_provider(
        func: Optional[Callable[..., Awaitable[RT]]] = None,
        auto_commit: Optional[bool] = False,
        nested: Optional[bool] = False
) -> RT:
    """
      ????????????:
        >>>
            @session_provider()
            async def func(session: AsyncSession):
                # ????????? session ??????
                result = await session.scalar(text('SELECT * from user'))
        >>>
            @session_provider()
            async def func(session: AsyncSession):
                # ?????? session ??????????????????????????????
                async with session.begin():
                    await session.scalar(text('SELECT * from user'))
        >>>
            @session_provider(auto_commit=True)
            async def func(session: AsyncSession):
                # ?????? session ??????????????????????????????
                result = await session.scalar(text('INSERT INTO user (name, age) VALUES ("foo", 123)'))
        >>>
            @session_provider(netsted=True)
            async def func(session: AsyncSession):
                # ?????? session ?????????????????????????????????
                result = await session.scalar(text('INSERT INTO user (name, age) VALUES ("foo", 123)'))
        >>>
            async def func(session: AsyncSession):
                result = await session.scalar(text('SELECT * from user'))
            # ??????????????????
            result = await session_provider(func, auto_commit=True)

    :param func:
    :param auto_commit:
    :param nested:
    :return:
    """
    if callable(func):
        return SessionProvider(auto_commit, nested)(func)
    else:
        return SessionProvider(auto_commit)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    """
    sqlite ??????????????????????????????????????????
    :param dbapi_connection:
    :param _connection_record:
    :return:
    """

    if isinstance(dbapi_connection, Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
