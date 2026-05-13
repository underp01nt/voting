from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import pages, upload

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(upload.router)
