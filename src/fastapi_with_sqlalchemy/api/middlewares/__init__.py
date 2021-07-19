from fastapi import FastAPI
from fastapi_with_sqlalchemy.api.middlewares.session import session_middleware
from starlette.middleware.base import BaseHTTPMiddleware


def init_middleware(app: FastAPI):
    app.add_middleware(BaseHTTPMiddleware, dispatch=session_middleware)
