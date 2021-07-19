import asyncio
from asyncio import Task
from typing import TYPE_CHECKING, Optional

from uvicorn import Server as UvicornServer, Config
from fastapi import FastAPI
from fastapi_with_sqlalchemy.api.middlewares import init_middleware
from fastapi_with_sqlalchemy.api.routers import init_router

if TYPE_CHECKING:
    from fastapi_with_sqlalchemy.server import Server


class RestAPI:

    def __init__(self, server: 'Server'):
        self._server = server

        self._app = FastAPI(db=self.server.db)

        uvicorn_config = Config(self.app)
        self._uvicorn_server = UvicornServer(uvicorn_config)
        self._server_task: Optional[Task] = None

    @property
    def app(self) -> FastAPI:
        return self._app

    @property
    def server(self) -> 'Server':
        return self._server

    def init(self):
        """Init app"""
        init_router(self.app)
        init_middleware(self.app)

    async def start(self) -> None:
        """"""
        self.init()
        loop = asyncio.get_running_loop()
        self._server_task = loop.create_task(self._uvicorn_server.serve())
        await asyncio.sleep(0.1)

    async def stop(self) -> None:
        """"""
        await self._uvicorn_server.shutdown()

    async def restart(self) -> None:
        """"""
