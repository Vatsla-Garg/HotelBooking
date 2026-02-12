from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.testing.provision import update_db_opts

from db.enums import Role
from db.models import DbHotel, DbHotelManager, DBFeature
from schemas import HotelBase, RateBase, UserBase


def create_hotel(request: HotelBase, current_user: UserBase, db: Session):
    if current_user.role == Role.GUEST:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    manager = db.query(DbHotelManager).filter(DbHotelManager.user_id == current_user.id).first()
    features = db.query(DBFeature).filter(
        DBFeature.id.in_(request.feature_ids)
    ).all()
    if len(features) != len(request.feature_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more feature IDs are invalid"
        )
    new_hotel = DbHotel(
        hotel_name=request.hotel_name,
        description=request.description,
        phone_number =request.phone_number,
        street_name =request.street_name,
        city =request.city,
        country =request.country,
        postcode =request.postcode,
        manager = manager,
        features = features
    )
    try:
        db.add(new_hotel)
        db.commit()
        db.refresh(new_hotel)
        return new_hotel
    except IntegrityError:
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

def update_hotel(hotel_id, request, current_user:UserBase, db: Session):
    if current_user.role == Role.GUEST:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    hotel = db.query(DbHotel).filter(DbHotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    if current_user.role == Role.HOTEL_MANAGER and hotel.manager_id != current_user.manager.id:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    #update features
    features = db.query(DBFeature).filter(
        DBFeature.id.in_(request.feature_ids)
    ).all()
    if len(features) != len(request.feature_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more feature IDs are invalid"
        )
    # db updates works only on table columns not relationships
    hotel.features = features # assign ORM objects directly, SQLAlchemy tracks the relationship changes
    try:
        updated_hotel = request.model_dump(exclude_unset=True, exclude={"feature_ids"})
        db.query(DbHotel).filter(DbHotel.id == hotel_id).update(updated_hotel)
        db.commit() #commit the ORM object, relationships included
        return db.query(DbHotel).filter(DbHotel.id == hotel_id).first()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hotel name and address already exists")

def delete_hotel(hotel_id: int, current_user:UserBase, db: Session):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    hotel = db.query(DbHotel).filter(DbHotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    db.delete(hotel)
    db.commit()

def rate_hotel(hotel_id: int, request: RateBase, current_user:UserBase ,db: Session):
    if current_user.role != Role.GUEST:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

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
    if hotel.rating_count == 0:
        return 0
    return round(hotel.rating_sum/hotel.rating_count,1)