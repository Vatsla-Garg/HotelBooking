from fastapi import HTTPException, FastAPI, Depends, status, APIRouter
from sqlalchemy.orm import Session
from typing import List
from db import db_hotel
from db.database import get_db
from db.enums import Rate
from schemas import HotelDisplay, HotelBase, HotelPatchBase, RateBase

router=APIRouter(
    prefix="/hotel",
    tags=["hotel"]
)
@router.post("/", response_model = HotelDisplay, description="create a hotel", summary="create a new hotel")
def create_hotel(request: HotelBase, db : Session = Depends(get_db)):
    return db_hotel.create_hotel(request, db)

@router.get("/", response_model=List[HotelDisplay], description="get all hotels", summary="get all hotels")
def get_all_hotel(db : Session = Depends(get_db)):
    return db_hotel.get_all_hotels(db)

@router.get("/{hotel_id}", response_model=HotelDisplay, description="get a hotel by id", summary="get a specific hotel")
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    return db_hotel.get_hotel(hotel_id, db)

@router.patch("/{hotel_id}", response_model= HotelDisplay, description="update a hotel by id", summary="update a hotel")
def update_hotel(hotel_id: int, request: HotelPatchBase, db: Session = Depends(get_db)):
    return db_hotel.update_hotel(hotel_id, request, db)

@router.patch("/rate/{hotel_id}", description="rate a hotel by id", summary="rate a hotel")
def rate_hotel(hotel_id: int, request:RateBase, db: Session = Depends(get_db)):
    return db_hotel.rate_hotel(hotel_id, request, db)

@router.delete( "{/hotel_id}",status_code=status.HTTP_204_NO_CONTENT, responses={status.HTTP_404_NOT_FOUND : {'description': "hotel does not exist"}, status.HTTP_204_NO_CONTENT:{"description":"hotel deleted successfully"}},description="delete a hotel by id", summary="delete a hotel")
def delete_hotel(hotel_id: int, db: Session = Depends(get_db)):
    return db_hotel.delete_hotel(hotel_id, db)

@router.get("/rating/{hotel_id}", description="get a hotel rating by id", summary="get a hotel rating")
def get_rating(hotel_id: int, db: Session = Depends(get_db)):
    return db_hotel.get_rating(hotel_id, db)
