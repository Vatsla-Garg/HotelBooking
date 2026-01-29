from db.database import Base
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Integer, String

#define table schemas for the db using SQLAlchemy ORM established in Base=declarative_base()
#every defined model should inherit from Base to be registered in the system's metadata

class DbUser(Base):
    __tablename__ = "users"
    id= Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
