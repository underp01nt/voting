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
    get_unencrypted_ballots_for_current_round,
    normalize_ballots,
    advance_election,
    insert_simulated_ballot,
)
from typing import Optional

router = APIRouter(prefix="/elections")
templates = Jinja2Templates(directory="templates")

""" RELEVANT REQUEST SCHEMAS """
class Election(BaseModel):
    name: str
    target_sizes: list[int]

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

class Tiers(BaseModel):
    tiers: list[list[str]]
    round_number: int

@router.post("/new")
def create_new_election_route(payload: Election, db=Depends(get_votes_db)):
    try:
        election_id = create_new_election(
            db, 
            name=payload.name, 
            target_sizes=payload.target_sizes, 
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
        nomination = nominate_candidate(db, candidate_id=payload.candidate_id, election_id=payload.election_id)
        return {
            "message": f"Nominated candidate {payload.candidate_id} for election {payload.election_id}",
            **nomination,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.post("/{election_id}/ballot")
def submit_tiers_list(request: Request, payload: Tiers, election_id: str, db=Depends(get_votes_db)):
    try:
        hashed_signature = request.session.get("hashed_signature", None)
        if not hashed_signature or not check_voter_in_election(hashed_signature, election_id, db):
            raise HTTPException(status_code=403, detail="Not authorized for this election")

        ballot_id = submit_ballot(hashed_signature, election_id, payload.tiers, payload.round_number, db)
        request.session["successful_submission"] = "Ballot successfully submitted"  # successful notification toast
        
        return {"ballot_id": ballot_id, "msg": "Ballot submission successful"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    
from services.processing import count_votes, get_candidates, get_target_sizes

@router.get("/{election_id}/candidates")
def get_candidates_route(election_id: str, db=Depends(get_votes_db)):
    return get_candidates(election_id, db)

# FOR SIMULATION PURPOSES ONLY
@router.post("/{election_id}/simulate")
def simulate_ballots_route(election_id: str, payload: Tiers, db=Depends(get_votes_db)):
   import uuid
   hashed_signature = f"SIM-{uuid.uuid4().hex}"
   insert_simulated_ballot(hashed_signature, election_id, payload.round_number, payload.tiers, db)

@router.get("/{election_id}/advance")
def advance_election_route(election_id: str, db=Depends(get_votes_db)):
    candidate_map = get_candidates(election_id, db)
    results = count_votes(
        candidates=[candidate["candidate_id"] for candidate in candidate_map], 
        ballots=normalize_ballots(get_unencrypted_ballots_for_current_round(election_id, db)),
        target=get_target_sizes(election_id, db),
        candidate_map=candidate_map,
    )

    next_round = results["Next Round"]
    if next_round["to_split"] is None:
        raise HTTPException(400, "Next round not available")
    
    advancing_candidates = next_round["advancing_candidates"]
    advance_election(election_id, advancing_candidates, db)

    return {"msg": "Election successfully advanced", "advancing_candidates": next_round["advancing_candidates"]}

# -> list[list[list[str]]]
@router.get("/{election_id}/standings")   # gets list of a collection of tiers defined by voters
def get_ballots(request: Request, election_id: str, round: int, db=Depends(get_votes_db)):
    hashed_signature = request.session.get("hashed_signature", None)
    if not hashed_signature: raise HTTPException(status_code=403, detail="Not authorized")
    elif not has_submitted_ballot(hashed_signature, election_id, db): raise HTTPException(status_code=403, detail="rlly bro?")

    cursor = db.cursor()
    cursor.execute("SELECT name FROM elections WHERE id = %s", (election_id,))
    name = cursor.fetchone()[0]

    candidate_map = get_candidates(election_id, db)
    results = count_votes(
        candidates=[candidate["candidate_id"] for candidate in candidate_map], 
        ballots=normalize_ballots(get_unencrypted_ballots_for_current_round(election_id, db)),
        target=get_target_sizes(election_id, db),
        candidate_map=candidate_map,
    )

    return templates.TemplateResponse(
        request=request, 
        name="standings.html", 
        context={
            "duration": results["Partition"]["duration"], 
            "fig": results["Partition"]["fig"],
            "heat": results["Partition"]["heat"],
            "name": name,
            "round": round,
        } 
    )