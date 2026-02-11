from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session
from sqlalchemy.testing.provision import update_db_opts

from db.models import DbHotel, DbHotelManager
from schemas import HotelBase, RateBase, UserBase
from utils import is_unique_constraint_error, is_not_found


def create_hotel(request: HotelBase, current_user: UserBase, db: Session):
    manager = db.query(DbHotelManager).filter(DbHotelManager.user_id == current_user.id).first()
    new_hotel = DbHotel(
        hotel_name=request.hotel_name,
        description=request.description,
        phone_number =request.phone_number,
        street_name =request.street_name,
        city =request.city,
        country =request.country,
        postcode =request.postcode,
        manager = manager
        #manager_id =manager.id
    )
    try:
        db.add(new_hotel)
        db.commit()
        db.refresh(new_hotel)
        return new_hotel
    except Exception as e:
        if is_unique_constraint_error(e):
            # DB rejected the transaction and raised IntegrityError, the transaction is "failed" but still open; any further queries or commits will fail until the session state is fixed
            db.rollback()
            #this clears the failed state in the session, resets the cnx
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Hotel name and address already exists")

def get_hotel(hotel_id: int, db: Session):
    hotel = db.query(DbHotel).filter(DbHotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return hotel

def get_hotel_by_manager(current_user: UserBase,db: Session):
    manager = db.query(DbHotelManager).filter(DbHotelManager.user_id == current_user.id).first()
    if not manager:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Manager not found")
    hotels= db.query(DbHotel).filter(DbHotel.manager_id == manager.id).all()
    return hotels

def get_all_hotels(db: Session):
    hotels = db.query(DbHotel).all()
    return hotels

def update_hotel(hotel_id, request, db: Session):
    try:
        updated_hotel=(
            db.query(DbHotel).filter(DbHotel.id == hotel_id).update(request.model_dump(exclude_unset=True))
        )
        if not updated_hotel:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
        db.commit()
        return db.query(DbHotel).filter(DbHotel.id == hotel_id).first()
    except Exception as e:
        db.rollback()
        if is_unique_constraint_error(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hotel name and address already exists")
        if is_not_found(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")

def delete_hotel(hotel_id: int, db: Session):
    hotel = db.query(DbHotel).filter(DbHotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    db.delete(hotel)
    db.commit()

def rate_hotel(hotel_id: int, request: RateBase, db: Session):
    hotel = db.query(DbHotel).filter(DbHotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    hotel.rating_count +=1
    hotel.rating_sum+=request.rate
    updated_hotel = {
        "rating_count" : hotel.rating_count,
        "rating_sum": hotel.rating_sum
    }
    # updated_hotel is already a dic; only Pydantic models has model_dump()
    db.query(DbHotel).filter(DbHotel.id == hotel_id).update(updated_hotel)
    db.commit()
    return db.query(DbHotel).filter(DbHotel.id == hotel_id).first()

def get_rating(hotel_id: int, db: Session):
    hotel= db.query(DbHotel).filter(DbHotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return round(hotel.rating_sum/hotel.rating_count,1)