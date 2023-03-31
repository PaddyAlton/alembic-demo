# models.py

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


DeclarativeBase = declarative_base()


class Countries(DeclarativeBase):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    iso2code = Column(String)
    iso3code = Column(String)

    def __repr__(self):
        return f"Country {self.name} ({self.iso2code})"


class Users(DeclarativeBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"))

    country = relationship(Countries)

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"
