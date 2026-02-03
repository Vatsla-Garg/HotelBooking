from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from db.database import get_db
from db.hash import Hash
from db.models import DbUser
from auth import oauth2
router = APIRouter(
    tags=["authentication"],
)
@router.post("/token")
def get_token(request:OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)):
    user = db.query(DbUser).filter(DbUser.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Wrong credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Incorrect password")
    access_token = oauth2.create_access_token(data={"user_id":user.id, "role":user.role, "username":user.username, "email":user.email})
    return {"access_token":access_token,"token_type":"bearer"}
