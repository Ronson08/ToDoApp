from .database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True)
    username = Column(String(200), unique=True)
    password = Column(String(255))
    first_name = Column(String(200))
    last_name = Column(String(100))
    role = Column(String(50))
    is_active = Column(Boolean, default=True)
    phone_number = Column(String(200))

    
class ToDo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(String(500))
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    