import asyncio

from fastapi_with_sqlalchemy.server import Server

if __name__ == '__main__':
    server = Server()
    asyncio.run(server.start())
