from fastapi import APIRouter, UploadFile, File, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from services.processing import count_votes, parse_csv
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

#  handles client csv data, processes data based on selected algorithms, renders algorithm results
#  args: (file: client csv data, algorithms: list of algorithms selected by client)
@router.post("/upload")
async def upload(request: Request, file: UploadFile=File(...), algorithms: Optional[list[str]]=Form(None)):
    if not algorithms:
        raise HTTPException(status_code=400, detail="Select at least one algorithm.")

    try:
        data = await file.read()
        rows = parse_csv(data)  # validate maybe?

        candidates, ballots = rows[0], rows[1:]
        election_outcome = count_votes(candidates, ballots)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Exception occurred: {e}")

    return templates.TemplateResponse(
        request=request,
        name="results.html",
        context={
            "results": election_outcome, 
            "ballots": ballots,
        })