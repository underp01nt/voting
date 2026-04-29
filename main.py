from ranked_pairs import ranked_pairs

from fastapi import FastAPI, UploadFile, File, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

from io import StringIO
import csv, time

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# TODO: verify client input, check for null entries, e.t.c.
def validate_client_csv_input(client_data: list[list[str]]) -> list[list[str]]:
    raise NotImplementedError()

@app.post("/upload")
async def upload(request:Request, file: UploadFile=File(...), algorithms: list[str]=Form(...)):

    # make text reader iterable per row
    def parse_csv(text: str) -> list[list[str]]:
        reader = csv.reader(StringIO(text))
        return [row for row in reader if row]

    try:
        data = await file.read()
        text = data.decode("utf-8")  # convert file content to text

        votes = parse_csv(text) #; validate_votes(votes)
        candidates = list(set(votes[0]))

        results = {}
        if "ranked_pairs" in algorithms:
            start = time.time()
            ranked_pairs_result = ranked_pairs(candidates, votes)
            end = time.time()

            results["ranked_pairs"] = {
                "ranking": ranked_pairs_result,
                "duration": end - start,
            }

        # if "proposal_method" in algorithms: 
        #   ...

    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad data read: {str(e)}")

    return {"algorithms_used": algorithms,
        "candidates": candidates,
        "experiments": results,}

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )