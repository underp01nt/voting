from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from db.factory import get_election_authority_db
from services.authentication import verify_voter
from pydantic import BaseModel
from services import crypto

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class TokenRequestForm:
    def __init__(self, 
                 name: str = Form(...), 
                 address: str = Form(...),
                 dob: str = Form(...),
                 ssn4: str = Form(...),
                 ):
        self.name = name
        self.address = address
        self.dob = dob
        self.ssn4 = ssn4

class BlindSignRequest(BaseModel):
    blinded_token: str

@router.post("/submit-request")
def submit_token_request(request: Request, form: TokenRequestForm = Depends(), db = Depends(get_election_authority_db)):
    eligibility_state = verify_voter(request, db, form.name, form.address, form.dob, form.ssn4)
    match eligibility_state: 
        case "valid eligibility": return RedirectResponse(url="/token", status_code=303) 
        case "eligibility already used": error_msg, status_code = "This user has already registered for a token", 400   # bad request
        case _: error_msg, status_code = "This user is not eligible for registration", 404     # not found

    return templates.TemplateResponse(
            request=request,
            name="verify-form.html",
            context={
                "verification_type": "manual",
                "error": error_msg,
            },
            status_code=status_code
        )

@router.post("/blind-sign")
def blind_sign(request: Request, payload: BlindSignRequest):
    blinded_token = payload.blinded_token
    
    # hash the blinded token
    blinded_token_hash =  crypto.hash_blinded_token(blinded_token)

    # TODO: check hash for duplicate, store in votes_db

    blinded_signature = crypto.sign_blinded_token(blinded_token)
    return {"blinded_signature": blinded_signature}