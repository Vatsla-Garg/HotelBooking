from sqlalchemy.orm import relationship

from db.database import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.sql.sqltypes import Integer, String
from datetime import datetime
from db.enums import Role
#define table schemas for the db using SQLAlchemy ORM established in Base=declarative_base()
#every defined model should inherit from Base to be registered in the system's metadata


class DbUser(Base):
    __tablename__ = "users"
    id= Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(Enum(Role), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    status = Column(String, default="ACTIVE")
    manager = relationship("DbHotelManager", back_populates="user", uselist=False, cascade="all, delete-orphan")
    guest = relationship("DbGuest", back_populates="user", uselist=False, cascade="all, delete-orphan")

class DbHotelManager(Base):
    __tablename__ = "hotel_managers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    user = relationship("DbUser", back_populates="manager", primaryjoin="DbUser.id==DbHotelManager.user_id")
    hotels = relationship("DbHotel", back_populates="manager")

class DbGuest(Base):
    __tablename__ = "guests"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer)
    rating_count = Column(Integer, default=0)
    rating_sum = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    user = relationship("DbUser", back_populates="guest",primaryjoin="DbUser.id==DbGuest.user_id")

class DbHotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    hotel_name = Column(String)
    description = Column(String)
    rating_count = Column(Integer, default=0)
    rating_sum = Column(Integer, default=0)
    phone_number = Column(String)
    street_name = Column(String)
    city = Column(String)
    country = Column(String)
    postcode = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    #the many side
    manager_id = Column(Integer, ForeignKey("hotel_managers.id"),nullable=False)
    manager = relationship("DbHotelManager", back_populates="hotels")
    #rooms
    #feature
    __table_args__ = (
        UniqueConstraint('hotel_name', 'street_name', 'city', name='uq_hotel_name_address'),
    )

class DBFeature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String, unique=True)
