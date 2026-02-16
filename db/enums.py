from enum import Enum

class Role(str, Enum):
    GUEST = "GUEST"
    HOTEL_MANAGER = "HOTEL_MANAGER"
    ADMIN = "ADMIN"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class BookingStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Rate(int, Enum):
    ONE=1
    TWO=2
    THREE=3
    FOUR=4
    FIVE=5

