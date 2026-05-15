from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/test", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )

@router.get("/", response_class=HTMLResponse)
async def auth_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )

@router.get("/cast", response_class=HTMLResponse)
async def cast(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cast.html",
    )

@router.get("/request", response_class=HTMLResponse)
async def request_token(request: Request, verification_type: Optional[str] = None):
    match verification_type:
        case "manual": template_name = "verify-form.html"
        case "government_id": template_name = "verify-photo.html"
        case _: template_name = "request.html"
    
    return templates.TemplateResponse(
        request=request,
        name= template_name,
        context={
            "verification_type": verification_type
        }
    )
