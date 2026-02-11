from db.enums import Role
from db.models import DbUser

print("MAIN FILE LOADED BOOKING PROJECT NOW")

from fastapi import FastAPI
from db import models
from db.database import engine, SessionLocal
from router import user, hotel,booking
from auth import authentication
app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def create_admin():
    db = SessionLocal()
    try:
        admin = db.query(DbUser).filter(DbUser.role == Role.ADMIN).first()
        if not admin:
            admin = DbUser(
                role = Role.ADMIN,
                email = "admin@gmail.com",
                password = "Azerty@123",
                username = "admin",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
    finally:
        db.close()

# registers the routes into the main FastAPI app
app.include_router(user.router)
app.include_router(booking.router)
#app.include_router(manager.router)
app.include_router(authentication.router)
app.include_router(hotel.router)

# create db if not created
# does not update existing tables if models are changed
# scans models and create missing tables
models.Base.metadata.create_all(engine)
