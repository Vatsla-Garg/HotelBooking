print("MAIN FILE LOADED BOOKING PROJECT")

from fastapi import FastAPI
from db import models
from db.database import engine
from router import user, manager
app = FastAPI()

# registers the routes into the main FastAPI app
app.include_router(user.router)
app.include_router(manager.router)

@app.get("/")
def index():
    return {"Hello": "World"}

# create db if not created
# does not update existing tables if models are changed
# scans models and create missing tables
models.Base.metadata.create_all(engine)
