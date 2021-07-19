from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, declared_attr, relationship


class CustomBase:
    """
    Customs DB base class
    """
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return cls.__name__.lower()  # pylint: disable=no-member


BaseModel = declarative_base(cls=CustomBase)


class User(BaseModel):
    name = Column(String(100))
    age = Column(Integer)

    addresses = relationship(
        'Address',
        backref='user'
    )


class Address(BaseModel):
    country = Column(String(100))
    city = Column(String(100))

    user_id = Column(Integer, ForeignKey('user.id'))
