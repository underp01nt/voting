from db.factory import get_votes_db
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from services.processing import (
    create_new_election, 
    add_new_candidate, 
    register_voter_to_election,
    nominate_candidate, 
    check_voter_in_election,
    submit_ballot,
    get_standings,
    has_submitted_ballot,
)
from typing import Optional

router = APIRouter(prefix="/elections")
templates = Jinja2Templates(directory="templates")

""" RELEVANT REQUEST SCHEMAS """
class Election(BaseModel):
    name: str
    target_size: int

class Candidate(BaseModel):
    name: str

class Voter(BaseModel):
    hashed_signature: str
    election_id: Optional[str]

class Nominee(BaseModel):
    candidate_id: str
    election_id : str

class Ballot(BaseModel):
    candidate_ids: list[str]
    round_number: int
    
@router.post("/new")
def create_new_election_route(payload: Election, db=Depends(get_votes_db)):
    try:
        election_id = create_new_election(
            db, 
            name=payload.name, 
            target_size=payload.target_size, 
        )

        return {"id": election_id, "message": "Election was successfully created"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.post("/add-candidate")
def add_new_candidate_route(payload: Candidate, db=Depends(get_votes_db)):
    try:
        candidate_id = add_new_candidate(name=payload.name, db=db)
        return {"id": candidate_id, "message": f"Candidate was successfully recorded in DB"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    
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
        raise HTTPException(status_code=500, detail=str(e)) from e
    
@router.post("/nominate")
def nominate_candidate_route(payload: Nominee, db=Depends(get_votes_db)):
    try: 
        nominate_candidate(db, candidate_id=payload.candidate_id, election_id=payload.election_id)
        return {"message": f"Nominated candidate {payload.candidate_id} for election {payload.election_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.post("/{election_id}/ballot")
def submit_or_update_ballot_route(request: Request, 
                                  payload: Ballot,
                                  election_id: str,
                                  db=Depends(get_votes_db)
                                  ):
    try:
        hashed_signature = request.session.get("hashed_signature", None)
        if not hashed_signature or not check_voter_in_election(hashed_signature, election_id, db):
            raise HTTPException(status_code=403, detail="Not authorized for this election")

        submit_ballot(hashed_signature, election_id, payload.candidate_ids, payload.round_number, db)
        request.session["successful_submission"] = "Ballot successfully submitted"  # successful notification toast

        return {"msg": "Ballot submission successful"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    
@router.get("/{election_id}/standings")
def get_standings_route(request: Request, election_id: str, round: int, db=Depends(get_votes_db)):
    hashed_signature = request.session.get("hashed_signature", None)
    if not hashed_signature: raise HTTPException(status_code=403, detail="Not authorized")
    elif not has_submitted_ballot(hashed_signature, election_id, db): raise HTTPException(status_code=403, detail="Ballot must be submitted first")

    return templates.TemplateResponse(
        request=request, 
        name="standings.html", 
        context={"standings": get_standings(election_id, round, db), "election_id": election_id, "round": round} 
    )
    