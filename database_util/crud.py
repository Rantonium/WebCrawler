
from sqlalchemy.orm import Session

from database_util.models import *
from database_util.schemas import *


def get_all_families(db: Session, limit: int, offset: int):
    return db.query(Family).offset(offset).limit(limit).all()


def get_family_by_hash_value(db: Session, hash_value: str):
    hash_pick = db.query(Hash).filter(Hash.name == hash_value).first()
    return db.query(Family).filter(Family.id == hash_pick.family_id).first()


def get_hashes_by_family_name(db: Session, family_name: str):
    family = db.query(Family).filter(Family.name == family_name).first()
    return db.query(Hash).filter(Hash.family_id == family.id).all()


def add_families_and_hashes(db: Session,  families_info: List[CreateAndUpdateFamily]):
    pass
    # new_car_info = PaginatedFamilyInfo(**car_info.dict())
    # db.add(new_car_info)
    # db.commit()
    # db.refresh(new_car_info)
    # return new_car_info

# def create_user(db: Session, user: schemas.UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.UserInfo(username=user.username, password=fake_hashed_password, fullname=user.fullname)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
