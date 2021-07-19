from typing import TypeVar

from fastapi_with_sqlalchemy.db.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
