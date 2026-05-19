from fastapi import APIRouter, Form, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from db.factory import get_election_authority_db, get_votes_db
from services.authentication import verify_voter, is_blinded_token_hash_unique
from pydantic import BaseModel
from services import crypto, processing

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

class VoterCredential(BaseModel):  # signed token must have signature
    token: str
    signature: str

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

@router.get("/public-key")
def get_public_key():
    return {
        "n": str(crypto.n),
        "e": str(crypto.e)
    }

@router.post("/blind-sign")
def blind_sign(payload: BlindSignRequest, db = Depends(get_votes_db)):
    blinded_token = payload.blinded_token
    
    # return the result of signed blinded token
    try:
        blinded_signature = crypto.sign_blinded_token(blinded_token)
        return {"blinded_signature": blinded_signature}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/login")
def login(payload: VoterCredential, db = Depends(get_votes_db)):
    # get token and signature
    token = payload.token
    signature = payload.signature

    if not crypto.verify_signature(token, signature):
        raise HTTPException(401, "Invalid credential")
    
    hashed_signature = crypto.hash_token_hex(signature)
    processing.insert_or_get_ballot(db, hashed_signature)

    return {"status": "authenticated", "redirect": "/cast"}
