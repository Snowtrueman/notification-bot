import os

import sqlalchemy.engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_directory = "db"
db_name = "remindmebot.db"


def get_db() -> sqlalchemy.engine.Engine:
    """
    Returns sqlalchemy engine instance.

    Returns:
        Engine instance.
    """

    if not os.path.exists(db_directory):
        os.mkdir(db_directory)

    engine = create_engine(f"sqlite:///{db_directory}/{db_name}?check_same_thread=False", echo=False)

    return engine


def get_session() -> sqlalchemy.orm.Session:
    """
    Returns sqlalchemy session instance.

    Returns:
        Session instance.
    """

    Session = sessionmaker(bind=get_db())
    session = Session()
    return session

