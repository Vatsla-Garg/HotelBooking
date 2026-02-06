from datetime import datetime
from typing import Literal
#Pydantic is a data validation library
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from db.enums import UserStatus, Role


# schema for data entering the API
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = EmailStr
    password: str = Field(..., min_length=8)
    role: Role
class HotelManager(BaseModel):
    id: int
    hotel_id: Optional[int]=None
    model_config = ConfigDict(from_attributes=True)

class Guest(BaseModel):
    id: int
    rating_sum: int
    rating_count: int
    booking_id: Optional[int]=None
    model_config = ConfigDict(from_attributes=True)
# schema for data leaving the API
class UserDisplay(BaseModel):
    id: int
    username: str
    email: str
    role: Role
    created_at: datetime
    updated_at: datetime
    status: UserStatus
    manager: Optional[HotelManager] = None
    guest:Optional[Guest] = None
    # Allow reading SQLAlchemy model attributes directly (Pydantic v2)
    model_config = ConfigDict(from_attributes=True)

class GetUserDisplay(BaseModel):
    id:int
    username: str
    email: str
    role: Role
    status: UserStatus
    manager: Optional[HotelManager] = None
    guest:Optional[Guest] = None
    model_config = ConfigDict(from_attributes=True)

class UserPatchBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str]= None
    status:Optional[UserStatus]= None


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
