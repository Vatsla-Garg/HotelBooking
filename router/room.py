from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import db_room
from db.database import get_db
from schemas import RoomBase, RoomDisplay, RoomPatchBase, UserBase


router = APIRouter(
    prefix="/room",
    tags=["room"]
)


@router.post(
    "/",
    response_model=RoomDisplay,
    summary="Create a room",
    description="Create a room for a hotel"
)
def create_room(
    request: RoomBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user)
):
    return db_room.create_room(request, current_user, db)


@router.get(
    "/hotel/{hotel_id}",
    response_model=List[RoomDisplay],
    summary="Get rooms by hotel",
    description="Get all rooms for a specific hotel"
)
def get_rooms_by_hotel(hotel_id: int, db: Session = Depends(get_db)):
    return db_room.get_rooms_by_hotel(hotel_id, db)


@router.get(
    "/{room_id}",
    response_model=RoomDisplay,
    summary="Get room by id",
    description="Get one room by room id"
)
def get_room(room_id: int, db: Session = Depends(get_db)):
    return db_room.get_room(room_id, db)


@router.patch(
    "/{room_id}",
    response_model=RoomDisplay,
    summary="Update room",
    description="Update room details"
)
def update_room(
    room_id: int,
    request: RoomPatchBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user)
):
    return db_room.update_room(room_id, request, current_user, db)


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete room",
    description="Delete a room by id"
)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user)
):
    return db_room.delete_room(room_id, current_user, db)
