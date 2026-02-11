from db.enums import Role
from db.models import DBFeature
from schemas import FeatureBase, UserBase
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


def add_new_feature(request: FeatureBase, db: Session):
    new_feature = DBFeature(
        feature= request.feature
    )
    try:
        db.add(new_feature)
        db.commit()
        db.refresh(new_feature)
        return new_feature
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="feature already exists")

def get_features(current_user: UserBase, db: Session):
    if current_user.role == Role.GUEST:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You do not have permission to access this resource")
    features = db.query(DBFeature).all()
    return features

def get_feature_by_id(feature_id: int, current_user: UserBase, db: Session):
    if current_user.role == Role.GUEST:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You do not have permission to access this resource")
    feature = db.query(DBFeature).filter(DBFeature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Feature not found")
    return feature

def update_feature(feature_id: int, request: FeatureBase, current_user: UserBase, db: Session):
    #only admin can update a feature
    #if current_user.role == Role.ADMIN:
    #    raise HTTPException(status_code= status.HTTP_403_FORBIDDEN,detail="You do not have permission to access this resource")
    feature = db.query(DBFeature).filter(DBFeature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Feature not found")
    db.query(DBFeature).filter(DBFeature.id == feature_id).update(request.dict())
    db.commit()
    updated_feature= db.query(DBFeature).filter(DBFeature.id == feature_id).first()
    return updated_feature

def delete_feature(feature_id: int, current_user: UserBase, db: Session):
    #only admin can delete a feature
    #if current_user.role == Role.ADMIN:
    #    raise HTTPException(status_code= status.HTTP_403_FORBIDDEN,detail="You do not have permission to access this resource")
    feature = db.query(DBFeature).filter(DBFeature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Feature not found")
    db.query(DBFeature).filter(DBFeature.id == feature_id).delete()
    db.commit()

