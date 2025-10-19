from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from .api.routers import router

app = FastAPI(title="PSA PathFinder Prototype", version="0.1.0")
app.include_router(router)

# Serve a minimal static UI
app.mount("/ui", StaticFiles(directory="web", html=True), name="ui")

@app.get("/")
def root():
    return RedirectResponse(url="/ui/")
