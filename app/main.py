from fastapi import FastAPI
from .api.routers import router

app = FastAPI(title="PSA PathFinder Prototype", version="0.1.0")
app.include_router(router)
