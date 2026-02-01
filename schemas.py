from typing import Literal
#Pydantic is a data validation library
from pydantic import BaseModel, Field, EmailStr, ConfigDict

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
    # Allow reading SQLAlchemy model attributes directly (Pydantic v2)
    model_config = ConfigDict(from_attributes=True)

class GetUserDisplay(BaseModel):
    username: str
    email: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class HotelManagerBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = EmailStr
    password: str = Field(..., min_length=8)
    hotel_id: int


class HotelManagerDisplay(BaseModel):
    id: int
    username: str
    email: str
    hotel_id: int
    model_config = ConfigDict(from_attributes=True)
