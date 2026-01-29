from sqlalchemy.orm.session import Session
from schemas import UserBase
from db.models import DbUser
from db.hash import Hash

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
