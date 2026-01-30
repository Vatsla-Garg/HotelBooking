from fastapi import FastAPI
from db import models
from db.database import engine
from router import user
app = FastAPI()

# registers the routes into the main FastAPI app
app.include_router(user.router)

@app.get("/")
def index():
    return {"Hello": "World"}

# create db if not created
# does not update existing tables if models are changed
# scans models and create missing tables
models.Base.metadata.create_all(engine)