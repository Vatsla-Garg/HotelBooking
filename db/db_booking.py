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

    if request.person_number < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person number should be greater than 0"
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
    ).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is unavailable for this hotel"
        )
    if not room.available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is not available"
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
    total_price = float(nights * room.price_per_night * 1)

    new_booking = DbBooking(
        user_id=current_user.id,
        hotel_id=request.hotel_id,
        room_id=request.room_id,
        checkin_date = request.checkin_date,
        checkout_date = request.checkout_date,
        person_number = request.person_number,
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

def delete_booking(booking_id, db:Session, user):
    if user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not authorized")
    if user.role == Role.ADMIN:
        booking = db.query(DbBooking).filter(
            DbBooking.id == booking_id
        ).first()
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="booking does not exist")
        db.delete(booking)
        db.commit()

    return {"message": "Entry deleted successfully"}


def cancel_booking(db: Session, booking_id: int, current_user):

    if current_user.role != Role.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only guests can cancel bookings"
        )

    booking = db.query(DbBooking).filter(
        DbBooking.id == booking_id,
        DbBooking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking does not exist"
        )


    if booking.booking_status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )

    booking.booking_status = BookingStatus.CANCELLED

    room = db.query(DbRoom).filter(DbRoom.id == booking.room_id).first()
    if room:
        room.available = True

    db.commit()
    db.refresh(booking)
    return booking