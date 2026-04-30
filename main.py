import argparse as ap
import pandas as pd
import votingutils

parser = ap.ArgumentParser()
parser.add_argument("--votes", "-v", default="", help="csv file of votes, where each row is a vote and each value is a candidate, in order")
parser.add_argument("--candidates", "-c", default="", help="file containing list of candidate names, or list of candidate names separated by commas")
args = parser.parse_args()

# Handle votes
votes = []

if not args.votes.endswith((".csv",".txt")):
    args.votes =input("Votes file? (enter if no):")
    
if not args.votes.endswith((".csv",".txt")):
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
            votes.append(line.strip().replace(" ","").split(","))
        f.close()
            
# Handle candidates
candidates = []
if not args.candidates:
    candidates = list(set(c for vote in votes for c in vote))
elif args.candidates.endswith((".csv",".txt")):
    with open(args.candidates) as f:
        for line in f:
            candidates.append(line.replace(" ","").strip())
            break
        f.close()
else:
    candidates = [c.strip() for c in args.candidates.split(",")]

print("Candidates:", candidates)
print("Pick an election method:")
print("(1) Proposal Method")
print("(2) Ranked Pairs")

while True:
    method = input()
    match method:
        case "1" | "pm" | "PM" | "proposal method" | "Proposal Method":
            from proposal_method import honest_election, plot_elections
            result, elections = honest_election(candidates, votes)
            if input("Plot multiround elections? (y/n) ") in ("y", "Y"):
                plot_elections(elections, block=True)
            if input("Save multiround elections? (y/n) ") in ("y", "Y"):
                elections.to_csv("./data/multiround_election_results.csv")
            break
        case "2" | "rp" | "RP" | "ranked pairs" | "Ranked Pairs":
            from ranked_pairs import ranked_pairs
            result = ranked_pairs(candidates, votes)
            break
        case _:
            print("Try again.")

print("Result:", votingutils.ranking_to_string(result))
if input("Save result? (y/n) ") in ("y", "Y"):
    votingutils.ranking_to_df(result).to_csv("./data/election_result.csv", index=False)
