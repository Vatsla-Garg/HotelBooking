from fastapi import APIRouter, Depends, HTTPException

from db.models import DbUser
from schemas import UserBase, UserDisplay
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_user


router = APIRouter(
    prefix="/user",
    tags=["user"]
)

# Create
@router.post(
    '/',
    response_model = UserDisplay,
    summary="Create a new user",
    description="Create a new user with username, email, role and password"
)
def create_user(request: UserBase, db:Session=Depends(get_db)):
    #save email in lowercase to ensure consistency
    request.email = request.email.lower()
    #check email uniqueness
    existing_user = db.query(DbUser).filter(DbUser.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        return db_user.create_user(db, request)


# Read

# Update

# Delete