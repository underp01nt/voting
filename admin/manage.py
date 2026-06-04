import argparse, requests
import ast
import random

ELECTIONS_MGMT_URL = "http://127.0.0.1:8000/elections"

def post(path: str, payload: dict) -> dict[str, str]:
    print("POST URL:", path)
    print("POST DATA:", payload)
    print()

    complete_path = ELECTIONS_MGMT_URL + path
    response = requests.post(complete_path, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()

# -make  
def create_election(name: str, target_sizes: str): 
    return post("/new", {"name": name, "target_sizes": ast.literal_eval(target_sizes)})

# -candidate  |  REQUIRES: name (of candidate)
def add_new_candidate(name: str): 
    return post("/add-candidate", {"name": name})

# -register  
def register_voter(hashed_signature: str, election_id: str):
    return post("/register-voter", {"hashed_signature": hashed_signature, "election_id": election_id})

# -nominate  
def nominate_candidate(candidate_id: str, election_id: str):
    return post("/nominate", {"candidate_id": candidate_id, "election_id": election_id})

def submit_simulated_ballot(election_id, round_number: int, tiers: list[list[str]]):
    return post(f"/{election_id}/simulate", {"round_number": round_number, "tiers": tiers})

def get_active_candidate_ids(election_id: str) -> list[str]:
    response = requests.get(f"{ELECTIONS_MGMT_URL}/{election_id}/candidates", timeout=5)
    response.raise_for_status()
    data = response.json()
    return [c["candidate_id"] for c in data]

def voter_to_tiers(voter: dict[str, float]) -> list[list[str]]:
    # sort candidates by score
    sorted_items = sorted(voter.items(), key=lambda x: x[1], reverse=True)

    tiers = []
    current_tier = [sorted_items[0][0]]
    last_score = sorted_items[0][1]

    for candidate, score in sorted_items[1:]:
        if abs(score - last_score) < 1e-6:
            current_tier.append(candidate)
        else:
            tiers.append(current_tier)
            current_tier = [candidate]
            last_score = score

    tiers.append(current_tier)
    return tiers

def generate_voter(candidates: list[str]) -> dict[str, float]: return {c: random.random() for c in candidates}
def simulate_ballots(candidates: list[str], voter_count: int) -> list[list[list[str]]]:
    ballots = []

    for _ in range(voter_count):
        voter = generate_voter(candidates)
        tiers = voter_to_tiers(voter)
        ballots.append(tiers)

    return ballots

def run_simulation(election_id: str, voter_count: int):
    candidates = get_active_candidate_ids(election_id)
    print(candidates)
    ballots = simulate_ballots(candidates, voter_count); print(ballots)
    round_number = 1

    for ballot in ballots:
        submit_simulated_ballot(election_id, round_number, ballot)

    return {"election_id": election_id, "voters": voter_count, "candidates": candidates}

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("identity")   # name of Election, Candidate, Voter hashed signature or Election ID (simulation only)

    # create new election
    parser.add_argument("-make", action="store_true")
    # register new candidate
    parser.add_argument("-candidate", action="store_true")
    # register a voter for a specific election
    parser.add_argument("-register", action="store_true")
    # nominate a candidate/representative for a specific election
    parser.add_argument("-nominate", action="store_true")
    # simulate a single round of an election
    parser.add_argument("-simulate", action="store_true")

    # params
    parser.add_argument("--target-sizes", type=str)
    parser.add_argument("--election-id", type=str)
    parser.add_argument("--candidate-id", type=str)
    parser.add_argument("--voter-count", type=int)

    args = parser.parse_args()

    if args.make: create_election(args.identity, args.target_sizes)
    elif args.candidate: add_new_candidate(args.identity)
    elif args.register: register_voter(args.identity, args.election_id)
    elif args.nominate: nominate_candidate(args.identity, args.election_id)
    elif args.simulate: run_simulation(args.identity, args.voter_count)