from fastapi import APIRouter, Form, Depends
from fastapi.templating import Jinja2Templates

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

# TODO: perform sql query on mock authority DB before presenting token gen prompt
@router.post("/submit-request")
def submit_token_request(form: TokenRequestForm = Depends()):
    return {
        "name": form.name, 
        "address": form.address, 
        "dob": form.dob, 
        "ssn4": form.ssn4
    }
