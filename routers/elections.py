from db.factory import get_votes_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from services.processing import create_new_election, add_new_candidate, register_voter_to_election
from typing import Optional

router = APIRouter(prefix="/elections")
templates = Jinja2Templates(directory="templates")

class Election(BaseModel):
    name: str
    target_size: int

class Candidate(BaseModel):
    name: str
    election_id: Optional[str]

class Voter(BaseModel):
    hashed_signature: str
    election_id: Optional[str]
    
@router.post("/new")
def create_new_election_route(payload: Election, db=Depends(get_votes_db)):
    try:
        election_id = create_new_election(
            db, 
            name=payload.name, 
            target_size=payload.target_size, 
        )

        return {"id": election_id, "message": "Election was created successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-candidate")
def add_new_candidate_route(payload: Candidate, db=Depends(get_votes_db)):
    try:
        candidate_id = add_new_candidate(
            name=payload.name, 
            election_id=payload.election_id,
            db=db
        )

        return {
            "id": candidate_id, 
            "message": f"Candidate was successfully added in DB for election {payload.election_id}" \
            if payload.election_id else "Candidate was successfully registered in DB"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/register-voter")
def register_voter_route(payload: Voter, db=Depends(get_votes_db)):
    try:
        ballot_id = register_voter_to_election(
            hashed_signature=payload.hashed_signature,
            election_id=payload.election_id, 
            db=db
        )
        return {"ballot_id": ballot_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))