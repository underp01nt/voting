from db.factory import get_votes_db
from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.crypto import aesgcm, aes_decrypt
from services.processing import get_elections, get_candidates, get_existing_ballot
from typing import Optional
import ast

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
    successful_submission = request.session.pop("successful_submission", None)
    if hashed_signature:
        active_elections: list[dict] = get_elections(hashed_signature, db)
        # print(active_elections)
        return templates.TemplateResponse(
            request=request, 
            name="dashboard.html",
            context = {"active_elections": active_elections, "successful_submission": successful_submission}
        )
    else: return RedirectResponse("/", status_code=303)

@router.get("/cast")            # id in this context is election_id
def cast_ballot(request: Request, id: str, db=Depends(get_votes_db)):
    hashed_signature = request.session.get("hashed_signature")
    if not hashed_signature: raise HTTPException(401, "Not authenticated")

    # existing ballot w/o encrypted_ballot => voter is registered for this election but no submission
    ballot = get_existing_ballot(hashed_signature, id, db)
    if not ballot: raise HTTPException(403, "Not registered for this election")

    election_name, _, encrypted_ballot, last_updated, round_number = ballot
    all_candidates = get_candidates(id, db)

    # aes_decrypt returns string, so eval that
    chosen_candidates = ast.literal_eval(aes_decrypt(aesgcm, encrypted_ballot)) if encrypted_ballot else []

    if chosen_candidates:  # if not empty, use current list to get list of name and id mappings 
        candidate_lookup = {candidate["candidate_id"]: candidate for candidate in all_candidates}
        sol_chosen_candidates: list[dict[str, str]] = []

        for chosen_candidate_id in chosen_candidates:
            candidate = candidate_lookup[chosen_candidate_id]
            sol_chosen_candidates.append({"name": candidate["name"], "candidate_id": chosen_candidate_id})

        chosen_candidates = sol_chosen_candidates

    return templates.TemplateResponse(
            request=request, 
            name="cast.html",
            context={
                "all_candidates": all_candidates,
                "chosen_candidates": chosen_candidates,  
                "election_id": id,
                "last_updated": last_updated or None,
                "election_name": election_name, 
                "round_number": round_number,
            }
        )

@router.get("/cast-tiers")            # id in this context is election_id
def cast_tiers(request: Request, id: str, db=Depends(get_votes_db)):
    return templates.TemplateResponse(
            request=request, 
            name="tiers.html",
            context={
                "all_candidates": get_candidates(id, db),
                "election_id": id,
                # "election_name": election_name, 
                # "round_number": round_number,
            }
        )


####################  TEST ROUTES  #######################

@router.get("/test-token", response_class=HTMLResponse)
def get_token(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="token.html",
    )

@router.get("/test-tiers", response_class=HTMLResponse)
def get_token(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="tiers.html",
    )

