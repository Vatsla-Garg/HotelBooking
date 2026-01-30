from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_manager
from schemas import HotelManagerBase, HotelManagerDisplay

router = APIRouter(
    prefix="/manager",
    tags=["manager"]
)


@router.post(
    "/",
    response_model=HotelManagerDisplay,
    summary="Create a hotel manager profile",
    description="Create a hotel manager profile"
)
def create_manager(request: HotelManagerBase, db: Session = Depends(get_db)):
    manager, error = db_manager.create_manager(db, request)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return manager


@router.get(
    "/",
    response_model=List[HotelManagerDisplay],
    summary="Get all managers",
    description="Get all hotel managers"
)
def get_all_managers(db: Session = Depends(get_db)):
    return db_manager.get_all_managers(db)


@router.get(
    "/{manager_id}",
    response_model=HotelManagerDisplay,
    summary="Get a manager",
    description="Get a specific manager by id"
)
def get_manager(manager_id: int, db: Session = Depends(get_db)):
    manager = db_manager.get_manager(db, manager_id)
    if not manager:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager does not exist")
    return manager


@router.delete(
    "/{manager_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a manager",
    description="Delete a manager profile"
)
def delete_manager(manager_id: int, db: Session = Depends(get_db)):
    success = db_manager.delete_manager(db, manager_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager does not exist")
