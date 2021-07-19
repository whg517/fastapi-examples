from starlette.requests import Request


async def session_middleware(request: Request, call_next):
    request.db = request.app.extra.get('db')
    response = await call_next(request)
    return response
