from datetime import datetime, date
from typing import Literal, List
#Pydantic is a data validation library
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from db.enums import UserStatus, Role, Rate,BookingStatus
from pydantic_extra_types.phone_numbers import PhoneNumber



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


class BookingBase(BaseModel):
    hotel_id: int
    checkin_date: date
    checkout_date: date
    person_number: int
    room_number: int

class BookingDisplay(BaseModel):
    id: int
    user_id: int
    hotel_id: int
    checkin_date: date
    checkout_date: date
    person_number: int
    room_number: int
    #room_id: int
    booking_status: BookingStatus
    created_at: datetime
    updated_at: datetime

class HotelBase(BaseModel):
    hotel_name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    phone_number: PhoneNumber
    street_name: str
    city: str
    country: str
    postcode: str

class HotelDisplay(BaseModel):
    id: int
    hotel_name: str
    description: str
    phone_number: str
    street_name: str
    city: str
    country: str
    postcode: str
    rating_count: int
    rating_sum: int
    created_at: datetime
    updated_at: datetime
    #manger
    #features
    #rooms
    model_config = ConfigDict(from_attributes=True)

class HotelPatchBase(BaseModel):
    hotel_name: Optional[str]= Field(default=None , min_length=1, max_length=50)
    description: Optional[str]= Field(default=None , min_length=1, max_length=500)
    phone_number: Optional[PhoneNumber] = None
    street_name: Optional[str]= None
    city: Optional[str]= None
    country: Optional[str]= None
    postcode: Optional[str]= None

class HotelRateDisplay(BaseModel):
    id: int
    rating_count: int
    rating_sum: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RateBase(BaseModel):
    rate: Rate

class FeatureBase(BaseModel):
    feature:str

class FeatureDisplay(BaseModel):
    id: int
    feature: str
