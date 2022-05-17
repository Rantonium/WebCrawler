from sqlalchemy.orm import Session

from database_util import models, schemas


def get_all_families(db: Session, limit: int, offset: int):
    return db.query(models.Family).offset(offset).limit(limit).all()


def get_family_by_hash_value(db: Session, hash_value: str):
    hash_pick = db.query(models.Hash).filter(models.Hash.name == hash_value).first()
    return db.query(models.Family).filter(models.Family.id == hash_pick.family_id).first()


def get_hashes_by_family_name(db: Session, family_name: str):
    family = db.query(models.Family).filter(models.Family.name == family_name).first()
    return db.query(models.Hash).filter(models.Hash.family_id == family.id).all()


def add_family(db: Session, name):
    db_family = models.Family(name=name)
    db.add(db_family)
    db.commit()
    db.refresh(db_family)
    return db_family


def add_hash_to_family(db: Session, hash_: schemas.CreateAndUpdateHash):
    db_hash = models.Hash(family_id=hash_.family_id, name=hash_.name, filesize=hash_.filesize, date=hash_.date)
    db.add(db_hash)
    db.commit()
    db.refresh(db_hash)
    return db_hash
