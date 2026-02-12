from typing import List
from fastapi import APIRouter,Depends, status
from sqlalchemy.orm import Session
from auth.oauth2 import get_current_user
from schemas import BookingDisplay, BookingBase, UserBase
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
def create_booking(request: BookingBase, db:Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    return db_booking.create_booking(db, request, current_user)

#read all the bookings

@router.get('/',
            response_model=List[BookingDisplay],
            summary="Get all bookings",
            description="Get all bookings"
            )
def get_all_bookings(db: Session = Depends(get_db)):
    return db_booking.get_all_bookings(db)

#read specific the bookings

@router.get('/me',
            response_model=List[BookingDisplay],
            summary="Get user bookings",
            description="Get user all bookings"
            )
def get_booking(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    return db_booking.get_bookings(db, current_user.id)

# Delete booking

@router.delete('/{booking_id}',
               summary='Delete a booking',
               description='Delete a booking',
               status_code=status.HTTP_204_NO_CONTENT,
               responses={status.HTTP_404_NOT_FOUND: {'description': 'Booking does not exist'},
                          status.HTTP_204_NO_CONTENT: {'description': 'Booking deleted successfully'}}
               )
def delete_booking(booking_id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    return db_booking.delete_booking(booking_id, db, current_user.id)
