import argparse as ap
import pandas as pd
import votingutils

parser = ap.ArgumentParser()
parser.add_argument("--votes", "-v", default="", help="csv file of votes, where each row is a vote and each value is a candidate, in order")
parser.add_argument("--candidates", "-c", default="", help="file containing list of candidate names, or list of candidate names separated by commas")
args = parser.parse_args()

# Handle candidates part 1
candidates = []
if args.candidates.endswith((".csv",".txt")):
    with open(args.candidates) as f:
        for line in f:
            candidates.append(line.strip())
            break
        f.close()
elif args.candidates:
    candidates = [c.strip() for c in args.candidates.split(",")]

# Handle votes
votes = []
    
if not args.votes.endswith((".csv",".txt")):
    if input("Generate random votes? (y/n) ") in ("y", "Y"):
        from votingutils import generate_random_votes
        if not candidates:
            candidates = input("Candidates (comma separated): ").split(",")
        num_voters = int(input("Number of voters? "))
        votes = generate_random_votes(candidates, num_voters)
    else:    
        while True:
            print("Manual input: enter comma separated list, enter blank to finish.")
            vote = input()
            if not vote:
                break
            votes.append(vote.split(","))

else:
    with open(args.votes) as f:
        for line in f:
            if line == "\n":
                continue
            votes.append(line.strip().split(","))
        f.close()
            
# Handle candidates part 2
if not candidates:
    candidates = list(set(c for vote in votes for c in vote))
    
if input("View Condorcet Graph? (y/n) ") in ("y", "Y"):
    from condorcet_cycles import draw_beat_graph
    draw_beat_graph(candidates, votes, display=True)


while True:
    print()
    print("Candidates:", candidates)
    print("Pick an election method:")
    print("(1) Proposal Method")
    print("(2) Ranked Pairs")
    print("(0) Exit")
    print()
    
    result = []
    method = input()
    match method:
        case "1" | "pm" | "PM" | "proposal method" | "Proposal Method":
            from proposal_method import honest_election, plot_elections
            result, elections = honest_election(candidates, votes)
            if input("Plot multiround elections? (y/n) ") in ("y", "Y"):
                plot_elections(elections, block=True)
            if input("Save multiround elections? (y/n) ") in ("y", "Y"):
                elections.to_csv("./data/multiround_election_results.csv")
        case "2" | "rp" | "RP" | "ranked pairs" | "Ranked Pairs":
            from ranked_pairs import ranked_pairs
            result = ranked_pairs(candidates, votes)
        case "0" | "e" | "E" | "exit" | "Exit":
            exit()
        case _:
            print("Try again.")
    print("Result:", votingutils.ranking_to_string(result))
    if input("Save result? (y/n) ") in ("y", "Y"):
        votingutils.ranking_to_df(result).to_csv("./data/election_result.csv", index=False)

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