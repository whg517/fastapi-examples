import functools
import inspect

from fastapi_with_sqlalchemy.db import scoping_session


def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print('start')
        result = func(*args, **kwargs)
        print('end')
        return result

    return wrapper


@decorator
def foo():
    """"""
    print('foo........')


if __name__ == '__main__':
    foo()
