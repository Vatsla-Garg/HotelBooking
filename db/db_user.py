from sqlalchemy.orm.session import Session
from schemas import UserBase
from db.models import DbUser
from db.hash import Hash
from fastapi import HTTPException

#create functionality to write to db
def create_user(db:Session, request: UserBase):
    new_user = DbUser(
        username=request.username,
        email=request.email,
        password=Hash.bcrypt(request.password),
        role = request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_all_users(db:Session):
    return db.query(DbUser).all()

def get_user(db:Session, user_id: int):
    return db.query(DbUser).filter(DbUser.id == user_id).first()
def get_user_by_email(db:Session, email: str):
    user= db.query(DbUser).filter(DbUser.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user

def update_user(db:Session, user_id:int, request: UserBase):
    user = db.query(DbUser).filter(DbUser.id == user_id)
    user.update({
        DbUser.username: request.username,
        DbUser.email: request.email,
        DbUser.password: Hash.bcrypt(request.password)
    })
    db.commit()
    return 'OK'

def delete_user(db:Session, user_id: int):
    user = db.query(DbUser).filter(DbUser.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True