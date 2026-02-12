from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from db.enums import Role
from db.models import DbRoom, DbHotel, DbHotelManager
from schemas import RoomBase, RoomPatchBase, UserBase


def _authorize_hotel_access(db: Session, hotel_id: int, current_user: UserBase):
    hotel = db.query(DbHotel).filter(DbHotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel not found"
        )

    if current_user.role == Role.ADMIN:
        return hotel

    if current_user.role != Role.HOTEL_MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )

    manager = db.query(DbHotelManager).filter(
        DbHotelManager.user_id == current_user.id
    ).first()
    if not manager or hotel.manager_id != manager.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )

    return hotel


def create_room(request: RoomBase, current_user: UserBase, db: Session):
    _authorize_hotel_access(db, request.hotel_id, current_user)

    new_room = DbRoom(
        hotel_id=request.hotel_id,
        room_number=request.room_number,
        room_type=request.room_type,
        price_per_night=request.price_per_night,
        is_active=request.is_active
    )
    try:
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        return new_room
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room already exists for this hotel"
        )


def get_room(room_id: int, db: Session):
    room = db.query(DbRoom).filter(DbRoom.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return room


def get_rooms_by_hotel(hotel_id: int, db: Session):
    return db.query(DbRoom).filter(DbRoom.hotel_id == hotel_id).all()


def update_room(room_id: int, request: RoomPatchBase, current_user: UserBase, db: Session):
    room = db.query(DbRoom).filter(DbRoom.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    _authorize_hotel_access(db, room.hotel_id, current_user)

    update_data = request.model_dump(exclude_unset=True)
    if not update_data:
        return room

    try:
        db.query(DbRoom).filter(DbRoom.id == room_id).update(update_data)
        db.commit()
        return db.query(DbRoom).filter(DbRoom.id == room_id).first()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room already exists for this hotel"
        )


def delete_room(room_id: int, current_user: UserBase, db: Session):
    room = db.query(DbRoom).filter(DbRoom.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    _authorize_hotel_access(db, room.hotel_id, current_user)
    db.delete(room)
    db.commit()
