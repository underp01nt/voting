from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from db.factory import get_election_authority_db
from services.authentication import verify_voter

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

@router.post("/submit-request")
def submit_token_request(request: Request, form: TokenRequestForm = Depends(), db = Depends(get_election_authority_db)):
    eligibility_state = verify_voter(request, db, form.name, form.address, form.dob, form.ssn4)
    # TODO: make templates for each eligibility case
    match eligibility_state: 
        case "valid eligibility": return RedirectResponse(url="/token", status_code=303) 
        case "eligibility already used": return {"status_code": -1}  
        case _: return {"status_code": 2}  # no records matched
