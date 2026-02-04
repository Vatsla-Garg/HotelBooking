from sqlalchemy.orm.session import Session
from schemas import UserBase, UserPatchBase
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

def patch_user(request:UserPatchBase, user_id: int, db:Session):
    if request.email:
        try:
            user = get_user_by_email(db, request.email)
        except HTTPException:
            user = None
        if user and user.id != user_id:
            raise HTTPException(status_code=400, detail="Email already exists")
    updated_rows = (
        db.query(DbUser)
        .filter(DbUser.id == user_id)
        .update(request.model_dump(exclude_unset=True))
    )

    if updated_rows == 0:
        raise HTTPException(status_code=404, detail="User does not exist")

    db.commit()
    return db.query(DbUser).filter(DbUser.id == user_id).first()

def delete_user(db:Session, user_id: int):
    user = db.query(DbUser).filter(DbUser.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True