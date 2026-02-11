from fastapi import APIRouter, status
from fastapi.params import Depends
from db import db_feature
from auth.oauth2 import get_current_user
from db.database import get_db
from schemas import UserBase, HotelDisplay, FeatureBase, FeatureDisplay
from typing import List
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/feautres",
    tags=["feautres"]
)

@router.post("/", description="add a new feautre")
def add_new_feature(request: FeatureBase, db: Session=Depends(get_db)):
    return db_feature.add_new_feature(request, db)

@router.get("/", response_model=List[FeatureDisplay])
def get_features(current_user:UserBase=Depends(get_current_user),db: Session=Depends(get_db) ):
    return db_feature.get_features(current_user, db)

@router.get("/{feature_id}", response_model=FeatureDisplay)
def get_feature(feature_id:int, current_user:UserBase=Depends(get_current_user), db: Session = Depends(get_db)):
    return db_feature.get_feature_by_id(feature_id, current_user, db)

@router.patch("/{feature_id}", response_model=FeatureDisplay)
def update_feature(feature_id:int, request: FeatureBase, current_user:UserBase=Depends(get_current_user), db: Session = Depends(get_db)):
    return db_feature.update_feature(feature_id, request, current_user, db)
@router.delete("/{feature_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_feature(feature_id:int, current_user:UserBase=Depends(get_current_user), db: Session = Depends(get_db)):
    return db_feature.delete_feature(feature_id, current_user, db)