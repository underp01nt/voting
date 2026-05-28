from db.factory import get_votes_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from services.processing import create_new_election
from services.utils import generate_id

router = APIRouter(prefix="/elections")
templates = Jinja2Templates(directory="templates")

class Election(BaseModel):
    name: str
    target_size: int
    apply_to_all: bool = False
    
@router.post("/create")
def create_election(payload: Election, db=Depends(get_votes_db)):
    try:
        election_id = create_new_election(
            db, 
            name=payload.name, 
            target_size=payload.target_size, 
            valid=True, 
            id=generate_id(16), 
            round=1,
            apply_to_all=payload.apply_to_all,
        )

        return {
            "id": election_id,
            "message": "Election was created successfully!"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))