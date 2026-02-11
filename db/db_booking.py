from datetime import date
from sqlalchemy.orm import session
from sqlalchemy.orm.session import Session
from schemas import BookingBase
from db.models import DbBooking
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
#create booking

def create_booking(db: Session, request: BookingBase, user_id: int) :
    if request.person_number < 1 or request.person_number > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person number should be greater than 0 and less than or equal to 3"
        )
    if request.checkin_date > request.checkout_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Checkin date should be lesser than or equal to checkout date"
        )
    if request.checkin_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Checkin date should be greater than or equal to today"
        )
    new_booking = DbBooking(
        user_id=user_id,
        hotel_id=request.hotel_id,
        checkin_date = request.checkin_date,
        checkout_date = request.checkout_date,
        person_number = request.person_number,
        room_number = request.room_number
    )
    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Booking already exists for hotel {request.hotel_id}"
        )


#get all bookings

def get_all_bookings(db: Session):
    return db.query(DbBooking).all()

#get specific bookings

def get_bookings(db:Session, user_id: int):
    return db.query(DbBooking).filter(DbBooking.user_id == user_id)

#Delete booking

def delete_booking(booking_id, db:Session, user_id: int):

    booking = db.query(DbBooking).filter(DbBooking.id == booking_id and DbBooking.user_id == user_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="booking does not exist")

    db.delete(booking)
    db.commit()
    return {"message": "Entry deleted successfully"}
