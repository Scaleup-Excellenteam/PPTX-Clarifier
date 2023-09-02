import os
import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UUID, func, event
from sqlalchemy.orm import relationship

from pptx_clarifier.definitions import uploads_directory, outputs_directory
from pptx_clarifier.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    uploads = relationship("Upload", back_populates="user", cascade="all, delete", lazy="subquery")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

    def __str__(self):
        return self.email


@event.listens_for(User, "after_insert")
def create_user_directory(mapper, connection, target):
    os.makedirs(os.path.join(uploads_directory, target.__str__()), exist_ok=True)
    os.makedirs(os.path.join(outputs_directory, target.__str__()), exist_ok=True)


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True)
    uid = Column(String, nullable=False, default=str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime, nullable=False, default=func.now())
    finish_time = Column(DateTime)
    status = Column(String, nullable=False, default="started")
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="uploads", lazy="subquery")

    def __repr__(self):
        return f"<Upload(id={self.id}, uid={self.uid}>"

    def get_upload_path(self):
        if self.user:
            return os.path.join(uploads_directory, self.user.__str__(), self.filename)
        else:
            return os.path.join(uploads_directory, self.filename)

    def get_output_path(self):
        base_filename, _ = os.path.splitext(self.filename)
        output_filename = f'{base_filename}.json'
        if self.user:
            return os.path.join(outputs_directory, self.user.__str__(), output_filename)
        else:
            return os.path.join(outputs_directory, output_filename)

    def explanation(self):
        if self.status != "finished":
            return None
        else:
            with open(self.get_output_path(), "r") as f:
                return f.read()

