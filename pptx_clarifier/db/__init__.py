import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import sessionmaker

root = sys.path[1]
# create database file if it doesn't exist
db_path = os.path.join(root, "pptx_clarifier", "db", "pptx_clarifier.db")
db_uri = f"sqlite:///{db_path}"
engine = create_engine(db_uri, echo=True)


class Base(DeclarativeBase):
    pass


def start_db():
    if not os.path.exists(db_path):
        open(db_path, "w+").close()
    Base.metadata.create_all(engine)

