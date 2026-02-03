from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from db.models import DbUser
from schemas import UserBase, UserDisplay, GetUserDisplay
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_user
from auth.oauth2 import oauth2_scheme, get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


# Create
@router.post(
    '/',
    response_model=UserDisplay,
    summary="Create a new user",
    description="Create a new user with username, email, role and password"
)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    #save email in lowercase to ensure consistency
    request.email = request.email.lower()
    #check email uniqueness
    existing_user = db.query(DbUser).filter(DbUser.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    else:
        return db_user.create_user(db, request)


# Read all users
@router.get('/',
            response_model=List[UserDisplay],
            summary="Get all users",
            description="Get all users"
            )
def get_all_users(db: Session = Depends(get_db)):
    return db_user.get_all_users(db)

@router.get('/{user_id}',
            response_model=GetUserDisplay,
            summary='Get a specific user',
            description="Get a specific user"
            )
def get_user(user_id: int, db: Session = Depends(get_db), current_user:UserBase=Depends(get_current_user)):
    user = db_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    return user



# Update

# Delete
@router.delete('/{user_id}',
               summary='Delete a user',
               description='Delete a user',
               status_code=status.HTTP_204_NO_CONTENT,
               responses={status.HTTP_404_NOT_FOUND: {'description': 'User does not exist'},
                          status.HTTP_204_NO_CONTENT: {'description': 'User deleted successfully'}}
               )
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success= db_user.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")