from ranked_pairs import ranked_pairs

from fastapi import FastAPI, UploadFile, File, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from plotly import graph_objects as go

from io import StringIO
import csv, time

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# TODO: verify client input, check for null entries, e.t.c.
def validate_client_csv_input(client_data: list[list[str]]) -> list[list[str]]:
    raise NotImplementedError()

def build_rank_table(standings: list[str]) -> go.Figure:
    rank_indices = list(range(1, len(standings) + 1))
    return go.Figure(data=go.Table(
        header=dict(values=["Rank", "Candidate"]),
        cells=dict(values=[rank_indices, standings])
    ))

#  handles client csv data, processes data based on selected algorithms, renders algorithm results
#  args: (file: client csv data, algorithms: list of algorithms selected by client)
@app.post("/upload")
async def upload(request: Request, file: UploadFile=File(...), algorithms: list[str]=Form(...)):

    # make text reader iterable per row
    def parse_csv(text: str) -> list[list[str]]:
        reader = csv.reader(StringIO(text))
        return [row for row in reader if row]

    try:
        data = await file.read()
        text: str = data.decode("utf-8")  # convert file content to text

        votes = parse_csv(text) #; validate_votes(votes)
        candidates = votes[0]

        results = {}
        if "ranked_pairs" in algorithms:
            start = time.time()
            ranked_pairs_result = ranked_pairs(candidates, votes)
            end = time.time()

            fig = build_rank_table(ranked_pairs_result)
            results["ranked_pairs"] = {
                # "ranking": ranked_pairs_result,
                "duration": end - start,
                "fig": fig.to_html(full_html=False, config={"responsive": True}),
            }
            
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad data read: {e}")

    return templates.TemplateResponse(
        request=request,
        name="results.html",
        context={
            "results_A": results["ranked_pairs"]["fig"],
        })

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )