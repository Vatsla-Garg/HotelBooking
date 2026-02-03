from db.database import Base
from sqlalchemy import Column, DateTime
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
    role = Role
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    status = Column(String, default="ACTIVE")

class DbHotelManager(Base):
    __tablename__ = "hotel_managers"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    hotel_id = Column(Integer)
