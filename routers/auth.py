from fastapi import APIRouter, Form, Depends
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
def submit_token_request(form: TokenRequestForm = Depends(), db = Depends(get_election_authority_db)):
    request_status = verify_voter(form.name, form.address, form.dob, form.ssn4, db)
    # TODO: make templates for these eligibility cases
    match request_status: 
        case "valid eligibility": return {"status_code": 0}  # successful redirect to token gen page
        case "eligibility already used": return {"status_code": -1}  
        case _: return {"status_code": 2}  # no records matched
