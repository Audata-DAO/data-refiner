from sqlalchemy import (
    VARCHAR,
    CheckConstraint,
    Column,
    Numeric,
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

# Base model for SQLAlchemy
Base = declarative_base()


# Define database models - the schema is generated using these
class UserRefined(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    age = Column(Integer, nullable=False)
    country_code = Column(VARCHAR(2), nullable=False)
    occupation = Column(VARCHAR(30), nullable=False)
    language_code = Column(VARCHAR(10), nullable=False)
    region = Column(VARCHAR(100), nullable=False)

    audio = relationship("AudioRefined", back_populates="user")

    __table_args__ = (CheckConstraint("age >= 0", name="check_age"),)

    @validates("age")
    def validate_age(self, _, value):
        if value < 0:
            raise ValueError("age must be a non-negative integer")
        return value


class AudioRefined(Base):
    __tablename__ = "audio"

    audio_id = Column(Integer, primary_key=True, autoincrement=True)

    audio_length = Column(Numeric, nullable=False)
    audio_source = Column(VARCHAR(10), nullable=False)
    audio_type = Column(VARCHAR(10), nullable=False)

    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    user = relationship("UserRefined", back_populates="audio")
