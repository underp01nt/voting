from db.factory import get_votes_db
from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.processing import get_elections, check_voter_in_election, get_candidates
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def auth_page(request: Request):
    if request.session.get("hashed_signature", None):
        return RedirectResponse("/dashboard", status_code=303)
    else:
        return templates.TemplateResponse(
            request=request,
            name="auth.html",
        )

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )

@router.get("/request", response_class=HTMLResponse)
def request_token(request: Request, verification_type: Optional[str] = None):
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

@router.get("/token", response_class=HTMLResponse)
def token(request: Request):
    if request.session.pop("allowed_token", None):
        return templates.TemplateResponse(
            request=request,
            name="token.html"
        )
    
    return RedirectResponse("/", status_code=303)

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db=Depends(get_votes_db)):
    hashed_signature = request.session.get("hashed_signature", None)
    if hashed_signature:
        active_elections: list[dict] = get_elections(hashed_signature, db)
        # print(active_elections)
        return templates.TemplateResponse(
            request=request, 
            name="dashboard.html",
            context = {"active_elections": active_elections}
        )
    else: return RedirectResponse("/", status_code=303)

@router.get("/cast")            # id in this context is election_id
def cast_ballot(request: Request, id: str, db=Depends(get_votes_db)):
    hashed_signature = request.session.get("hashed_signature")

    if not hashed_signature: raise HTTPException(401, "Not authenticated")
    elif not check_voter_in_election(hashed_signature, id, db):
        raise HTTPException(403, "Not registered for this election")

    all_candidates = get_candidates(id, db); print(all_candidates)
    return templates.TemplateResponse(
            request=request, 
            name="cast.html",
            context={
                "all_candidates": all_candidates,
                "chosen_candidates": [],   # TODO: work on voter resubmission
                "election_id": id,
            }
        )

####################  TEST ROUTES  #######################

@router.get("/test-cast", response_class=HTMLResponse)
def test_cast(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cast.html",
    )

@router.get("/test-token", response_class=HTMLResponse)
def get_token(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="token.html",
    )

@router.get("/test-tiers", response_class=HTMLResponse)
def test_tiers(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="tiers.html"
    )