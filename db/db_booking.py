from sqlalchemy.orm import session
from sqlalchemy.orm.session import Session
from schemas import BookingBase
from db.models import DbBooking



def create_booking(db: Session, request: BookingBase) :
    new_booking = DbBooking(
        user_id=request.user_id,
        hotel_id=request.hotel_id,
        checkin_date = request.checkin_date,
        checkout_date = request.checkout_date,
        person_number = request.person_number
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

