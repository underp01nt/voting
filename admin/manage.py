import argparse, requests

ELECTIONS_MGMT_URL = "http://127.0.0.1:8000/elections"

# -make  |  identity = hashed_signature
def create_election(identity: str, target_size: int): 
    try:
        payload = {"name": identity, "target_size": target_size}
        response = requests.post(f"{ELECTIONS_MGMT_URL}/new", json=payload)
        # print(response.status_code); print(response.text)
        response.raise_for_status()

        data = response.json()
        print(f"Created election ID: {data['id']}")
        print(data["message"])
    
    except requests.RequestException as e:
        print(e)

# TODO: decouple election_id from candidate addition
# -candidate  |  identity = name
def add_new_candidate(identity: str, election_id: str): 
    try:
        payload = {"name": identity, "election_id": election_id}
        response = requests.post(f"{ELECTIONS_MGMT_URL}/add-candidate", json=payload)
        response.raise_for_status()

        data = response.json()
        print(f"Created candidate ID: {data["id"]}")
        print(data["message"])

    except requests.RequestException as e:
        print(e)

# -register  |  identity = hashed_signature
def register_voter(identity: str, election_name: str, election_id: str):
    try:
        payload = {"hashed_signature": identity, "election_name": election_name, "election_id": election_id}
        response = requests.post(f"{ELECTIONS_MGMT_URL}/register-voter", json=payload)
        response.raise_for_status()

        data = response.json()
        print(f"Successfully registered voter with ballot ID: {data["ballot_id"]}")
        print(data["message"])
        
    except requests.RequestException as e:
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("identity")   # name of Election, Candidate, or Voter hashed signature

    # create new election
    parser.add_argument("-make", action="store_true")
    # register new candidate
    parser.add_argument("-candidate", action="store_true")
    # register a voter for a specific election
    parser.add_argument("-register", action="store_true")

    # params
    parser.add_argument("--target-size", type=int)
    parser.add_argument("--election", type=str)
    parser.add_argument("--election-id", type=str)

    args = parser.parse_args()

    if args.make: create_election(args.identity, args.target_size)
    elif args.candidate: add_new_candidate(args.identity, args.election_id)
    elif args.register: register_voter(args.identity, args.election, args.election_id)