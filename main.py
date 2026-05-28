from config import settings
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from routers import pages
from routers import auth, upload, elections
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(upload.router)
app.include_router(auth.router)
app.include_router(elections.router)

if settings.SESSION_MIDDLEWARE_SECRET_KEY is None:
    raise RuntimeError("SESSION_MIDDLEWARE_SECRET_KEY not set")
else:
    app.add_middleware(
        SessionMiddleware, 
        secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY
    )