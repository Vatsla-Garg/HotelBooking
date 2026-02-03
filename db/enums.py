from enum import Enum

class Role(str, Enum):
    GUEST = "GUEST"
    HOTEL_MANAGER = "HOTEL_MANAGER"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"