from datetime import date
from sqlalchemy.orm.session import Session
from schemas import BookingBase
from db.models import DbBooking, DbRoom
from db.enums import Role, BookingStatus
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
#create booking

def create_booking(db: Session, request: BookingBase, current_user) :
    if current_user.role != Role.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only guests can create bookings"
        )

    if request.person_number < 1 or request.person_number > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person number should be greater than 0 and less than or equal to 3"
        )
    if request.room_count < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room count should be greater than 0"
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

    room = db.query(DbRoom).filter(
        DbRoom.id == request.room_id,
        DbRoom.hotel_id == request.hotel_id,
        DbRoom.available.is_(True)
    ).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is unavailable for this hotel"
        )

    overlapping_booking = db.query(DbBooking).filter(
        DbBooking.room_id == request.room_id,
        DbBooking.booking_status == BookingStatus.CONFIRMED,
        DbBooking.checkin_date < request.checkout_date,
        DbBooking.checkout_date > request.checkin_date
    ).first()
    if overlapping_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking dates overlap with an existing confirmed booking"
        )

    nights = (request.checkout_date - request.checkin_date).days
    total_price = float(nights * room.price_per_night * request.room_count)

    new_booking = DbBooking(
        user_id=current_user.id,
        hotel_id=request.hotel_id,
        room_id=request.room_id,
        checkin_date = request.checkin_date,
        checkout_date = request.checkout_date,
        person_number = request.person_number,
        room_count=request.room_count,
        total_price=total_price,
        booking_status=BookingStatus.CONFIRMED
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
    return db.query(DbBooking).filter(DbBooking.user_id == user_id).all()

#Delete booking

def delete_booking(booking_id, db:Session, user_id: int):
    booking = db.query(DbBooking).filter(
        DbBooking.id == booking_id,
        DbBooking.user_id == user_id
    ).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="booking does not exist")

    db.delete(booking)
    db.commit()
    return {"message": "Entry deleted successfully"}
