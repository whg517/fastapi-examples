from typing import Callable, Optional

from dynaconf import Dynaconf
from fastapi_with_sqlalchemy.api import RestAPI

from fastapi_with_sqlalchemy.config import settings
from fastapi_with_sqlalchemy.db import Database, init_db


class Server:

    def __init__(self):
        self._settings = settings
        self._db = init_db(self.settings)
        self._rest_api = RestAPI(self)

        self._tasks = []

    @property
    def settings(self) -> Dynaconf:
        return self._settings

    @property
    def rest_api(self):
        return self._rest_api
    @property
    def tasks(self):
        return self._tasks

    @property
    def db(self) -> Database:
        return self._db

    async def start(self) -> None:
        """Start some module."""
        await self._rest_api.start()

    async def run(self) -> None:
        """Run server"""
        try:
            await self.start()
        finally:
            await self.stop()

    def add_task(self, func: Callable) -> None:
        self.tasks.append(func)

    async def stop(self) -> None:
        await self._rest_api.stop()
        await self.db.close()
