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

    wallet_address = Column(String, primary_key=True)
    birth_year = Column(Integer, nullable=False)
    birth_month = Column(String, nullable=False)
    occupation = Column(VARCHAR(30), nullable=False)
    country = Column(String, nullable=False) # TODO
    region = Column(String, nullable=False)

    audio = relationship("AudioRefined", back_populates="user")

    __table_args__ = (CheckConstraint("birth_year >= 1900", name="check_age"),)

    @validates("birth_year")
    def validate_birth_year(self, _, value):
        if value < 0:
            raise ValueError("birth year must be a non-negative integer")
        return value


class AudioRefined(Base):
    __tablename__ = "audio"

    audio_id = Column(Integer, primary_key=True, autoincrement=True)

    language_code = Column(VARCHAR(10), nullable=False)
    audio_length = Column(Numeric, nullable=False)
    audio_source = Column(VARCHAR(10), nullable=False)
    audio_type = Column(VARCHAR(10), nullable=False)

    wallet_address = Column(String, ForeignKey("users.wallet_address"), nullable=False)
    user = relationship("UserRefined", back_populates="audio")
