from fastapi import FastAPI
from fastapi_with_sqlalchemy.api.routers import user


def init_router(app: FastAPI):
    app.include_router(user.router)
