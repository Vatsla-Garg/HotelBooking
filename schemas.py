from pydantic import BaseModel
class UserBase(BaseModel):
    username: str
    email: str
    password: str
    role: str

class UserDisplay(BaseModel):
    username: str
    email: str
    role: str
    class Config():
        orm_mode = True