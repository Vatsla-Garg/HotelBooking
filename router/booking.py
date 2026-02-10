from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from schemas import BookingDisplay, BookingBase
from db.database import get_db
from db import db_booking

router = APIRouter(
    prefix="/booking",
    tags=["booking"]
)

# Create
@router.post(
    '/',
    response_model=BookingDisplay,
    summary="Create a new booking",
    description="Create a new booking with checkin date, checkout date, number of persons and rooms"
)
def create_booking(request: BookingBase, db:Session = Depends(get_db)):
    return db_booking.create_booking(db, request)
