print("MAIN FILE LOADED BOOKING PROJECT NOW")

from fastapi import FastAPI
from db import models
from db.database import engine
from router import user, manager, hotel,booking
from auth import authentication
app = FastAPI()

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
