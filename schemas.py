from typing import Literal
#Pydantic is a data validation library
from pydantic import BaseModel, Field, EmailStr

# schema for data entering the API
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = EmailStr
    password: str = Field(..., min_length=8)
    role: Literal["guest","hotel manager"]

# schema for data leaving the API
class UserDisplay(BaseModel):
    username: str
    email: str
    role: str
    # without this line, Pydantic would crash because it wouldn't know how to extract data from the complex database result
    # pydantic only speaks "Dictionary," but your database speaks "SQLAlchemy Object"; orm_mode = True gives Pydantic the ability to translate the database object into a format it understands.
    class Config:
        orm_mode = True