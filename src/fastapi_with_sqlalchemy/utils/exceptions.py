from typing import Optional


class FastAPIWithSqlalchemyError(Exception):
    """SpiderkeeperError"""

    def __init__(self, detail: str):
        """
        :param detail:
        """
        self.detail = detail
        super().__init__(detail)

    def __repr__(self):
        """repr"""
        return f'{self.__class__.__name__}("detail"={self.detail})'


class ObjectNotFound(FastAPIWithSqlalchemyError):
    """
    Object does not exist.
    """

    def __init__(
            self,
            detail: Optional[str] = 'Object does not exist!',
    ):
        super().__init__(detail)
