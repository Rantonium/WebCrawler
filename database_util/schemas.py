import datetime
from typing import List

from pydantic import BaseModel


class CreateAndUpdateFamily(BaseModel):
    name: str


class Family(CreateAndUpdateFamily):
    id: int

    class Config:
        orm_mode = True


class PaginatedFamilyInfo(BaseModel):
    limit: int
    offset: int
    data: List[Family]


class CreateAndUpdateHash(BaseModel):
    family_id: int
    name: str
    filesize: int
    date: datetime.datetime


class Hash(CreateAndUpdateHash):
    id: int

    class Config:
        orm_mode = True


class PaginatedHashInfo(BaseModel):
    limit: int
    offset: int
    data: List[Hash]
