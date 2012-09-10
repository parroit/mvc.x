from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import  String, Integer
from sqlalchemy.orm import relation

def init(Base):
    class UserRole(Base):
        __tablename__ = 'user_roles'


        user_id = Column(String, ForeignKey('users.username'),primary_key=True)
        #user = relation("User")

        role_id = Column(String, ForeignKey('roles.role_name'),primary_key=True)
        role = relation("Role")

    return UserRole