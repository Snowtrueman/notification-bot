import datetime
from db import get_db
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Time, Boolean


Base = declarative_base(bind=get_db())


class Users(Base):
    """
    User model.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id = Column(Integer, nullable=False, unique=True)
    telegram_user_name = Column(String, nullable=False)
    chat_id = Column(Integer, nullable=False, unique=True)
    timezone = Column(String, nullable=False, default="Europe/Moscow")
    language = Column(String, nullable=False, default="ru")
    notifications_from = Column(Time, nullable=False, default=datetime.datetime.strptime("09:00:00", "%H:%M:%S").time())
    notifications_to = Column(Time, nullable=False, default=datetime.datetime.strptime("20:00:00", "%H:%M:%S").time())
    muted = Column(Boolean, nullable=False, default=False)

    user_todos = relationship("ToDos", backref="users", cascade="all")


class ToDos(Base):
    """
    Tasks model related to User model.
    """

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    todo = Column(String, nullable=False)
    todo_date = Column(Date, nullable=False)
