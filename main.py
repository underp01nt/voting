from ranked_pairs import ranked_pairs

from fastapi import FastAPI, UploadFile, File, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from plotly import graph_objects as go

from io import StringIO
from typing import Optional
import csv, time

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# TODO: verify client input, check for null entries, e.t.c.
def validate_client_csv_input(client_data: list[list[str]]) -> list[list[str]]:
    raise NotImplementedError()

def build_heat_map(candidates: list[str], votes: list[list[str]]) -> go.Figure:
    pairs = {a: {b: 0 for b in candidates} for a in candidates}
    for vote in votes:
        for i in range(len(vote)):  #  i > j, get number of voters preferred (or after) candidate i
            for j in range(i + 1, len(vote)):
                pairs[vote[i]][vote[j]] += 1

    # build matrix based on pairwise match-up scores
    mat = [[pairs[a][b] for b in candidates] for a in candidates]

    heat = go.Figure(data=go.Heatmap(z=mat, x=candidates, y=candidates, colorscale="Blues", zmin=0))
    heat.update_layout(
        title={"text": "Pairwise Comparisons (Vertical vs. Horizontal)", "x": 0.5}, 
        yaxis=dict(scaleanchor="x"), width=500, height=500,
    )
    return heat

def build_rank_table(votes: list[str]) -> go.Figure:
    num_candidates = len(votes)
    rank_indices = list(range(1, num_candidates + 1))
    fig = go.Figure(data=go.Table(
        header=dict(values=["Rank", "Candidate"]),
        cells=dict(values=[rank_indices, votes])
    ))

    fig.update_layout(title={"text": "Final Ranking", "x": 0.5}, height=180 + num_candidates * 30)
    return fig

#  handles client csv data, processes data based on selected algorithms, renders algorithm results
#  args: (file: client csv data, algorithms: list of algorithms selected by client)
@app.post("/upload")
async def upload(request: Request, file: UploadFile=File(...), algorithms: Optional[list[str]]=Form(None)):
    if not algorithms:
        raise HTTPException(status_code=400, detail="Select at least one algorithm.")

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
            heat = build_heat_map(candidates, votes)

            results["Ranked pairs"] = {
                # "ranking": ranked_pairs_result,
                "duration": end - start,
                "fig": fig.to_html(full_html=False, config={"responsive": True}),
                "heat": heat.to_html(full_html=False, config={"responsive": True})
            }
            
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Exception occurred: {e}")

    return templates.TemplateResponse(
        request=request,
        name="results.html",
        context={
            "results": results,
            "votes": votes,
        })

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )