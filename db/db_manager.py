from sqlalchemy.orm.session import Session
from db.models import DbHotelManager
from db.hash import Hash
from schemas import HotelManagerBase


def create_manager(db: Session, request: HotelManagerBase):
    new_manager = DbHotelManager(
        username=request.username,
        email=request.email.lower(),
        password=Hash.bcrypt(request.password),
        hotel_id=request.hotel_id,
    )
    db.add(new_manager)
    db.commit()
    db.refresh(new_manager)
    return new_manager, None


def get_all_managers(db: Session):
    return db.query(DbHotelManager).all()


def get_manager(db: Session, manager_id: int):
    return db.query(DbHotelManager).filter(DbHotelManager.id == manager_id).first()


def delete_manager(db: Session, manager_id: int):
    manager = db.query(DbHotelManager).filter(DbHotelManager.id == manager_id).first()
    if not manager:
        return False
    db.delete(manager)
    db.commit()
    return True
