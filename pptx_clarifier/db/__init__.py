import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import sessionmaker

# Get the root directory of the project
root = sys.path[1]

# Create the path to the SQLite database file
db_path = os.path.join(root, "pptx_clarifier", "db", "pptx_clarifier.db")
# Create the SQLite database URI
db_uri = f"sqlite:///{db_path}"
# Create an SQLAlchemy engine
engine = create_engine(db_uri, echo=True)

# Define a base class for declarative models
class Base(DeclarativeBase):
    pass

# Function to start the database
def start_db():
    # Create the database file if it doesn't exist
    if not os.path.exists(db_path):
        open(db_path, "w+").close()
    # Create the tables in the database
    Base.metadata.create_all(engine)
