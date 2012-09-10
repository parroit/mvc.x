from sqlalchemy.schema import Column
from sqlalchemy.types import  String, Boolean

def init(Base):
    class Role(Base):
        __tablename__ = 'roles'

        role_name = Column(String, primary_key=True)
        description = Column(String)

    return Role