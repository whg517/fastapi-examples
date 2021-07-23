"""Routers"""
from fastapi import FastAPI, APIRouter
from fastapi_with_sqlalchemy.api.routers import user


def router_v1() -> APIRouter:
    """APi v1"""
    router = APIRouter()
    # 注意：在这里不能通过使用 `prefix='/users'` 达到省略 user.router
    # 中视图函数中不需要标 '/user' 前缀的目的（@get('/{pk}')）
    # 因为在 post 的路由视图中， `@post('/')` 搭配 `prefix='/users'`
    # 会自动生成一个 `'/users/'` 的路由，但是 `@put('/{pk}') 会生成
    # `/users/{pk}` 的路由。
    # 这么做会造成生成的路由有的包含最后的斜杠，有的没有。
    # 在进行 post 的操作是，如果使用 `/users` 路径操作，会直接返回
    # 307 的重定向，并且造成 body 里的数据丢失。
    #
    # 更详细的逻辑，请阅读 `starlette.routing.router.__call__`
    # 方法中的逻辑。
    router.include_router(user.router, tags=['User'])

    return router


def init_router(app: FastAPI) -> None:
    """
    Init router to Fastapi
    :param app:
    :return:
    """
    app.include_router(router_v1(), prefix='/api/v1')
