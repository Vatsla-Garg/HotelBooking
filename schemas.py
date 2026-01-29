from typing import Literal
from pydantic import BaseModel, Field, EmailStr
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = EmailStr
    password: str = Field(..., min_length=8)
    role: Literal["guest","hotel manager"]

class UserDisplay(BaseModel):
    username: str
    email: str
    role: str
    class Config:
        orm_mode = True