from sqlalchemy.orm import relation
from sqlalchemy.schema import Column
from sqlalchemy.types import  String, Boolean

def init(Base):
    class User(Base):
        __tablename__ = 'users'

        username = Column(String, primary_key=True)
        fullname = Column(String)
        password = Column(String)
        email = Column(String)
        confirmed = Column(Boolean)
        admin = Column(Boolean)
        #roles = relation("UserRole", cascade="all, delete, delete-orphan")


    return User