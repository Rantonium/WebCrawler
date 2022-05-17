from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import String, Integer, DateTime
from sqlalchemy.orm import relationship
from database_util.database_config import Base


class Family(Base):
    __tablename__ = "family"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    hashes = relationship("Hash")


class Hash(Base):
    __tablename__ = "hash"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey('family.id'))
    name = Column(String)
    filesize = Column(Integer)
    date = Column(DateTime)

