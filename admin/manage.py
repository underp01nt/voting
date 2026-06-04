import argparse, requests
import ast

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

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("identity")   # name of Election, Candidate, or Voter hashed signature

    # create new election
    parser.add_argument("-make", action="store_true")
    # register new candidate
    parser.add_argument("-candidate", action="store_true")
    # register a voter for a specific election
    parser.add_argument("-register", action="store_true")
    # nominate a candidate/representative for a specific election
    parser.add_argument("-nominate", action="store_true")

    # params
    parser.add_argument("--target-sizes", type=str)
    parser.add_argument("--election-id", type=str)
    parser.add_argument("--candidate-id", type=str)

    args = parser.parse_args()

    if args.make: create_election(args.identity, args.target_sizes)
    elif args.candidate: add_new_candidate(args.identity)
    elif args.register: register_voter(args.identity, args.election_id)
    elif args.nominate: nominate_candidate(args.identity, args.election_id)
