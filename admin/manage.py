import argparse, requests

ELECTIONS_MGMT_URL = "http://127.0.0.1:8000/elections"

def create_election(name: str, target_size: int, apply_to_all: bool): 
    try:
        payload = {"name": name, "target_size": target_size, "apply_to_all": apply_to_all}
        response = requests.post(f"{ELECTIONS_MGMT_URL}/new", json=payload)
        # print(response.status_code); print(response.text)
        response.raise_for_status()

        data = response.json()

        print(f"Created election ID: {data['id']}")
        print(data["message"])
    
    except requests.RequestException as e:
        print(e)

def add_new_candidate(name: str, election_name: str, election_id: str):
    try:
        payload = {"name": name, "election_name": election_name, "election_id": election_id}
        response = requests.post(f"{ELECTIONS_MGMT_URL}/add-candidate", json=payload)
        response.raise_for_status

        data = response.json()  ; print(data)

        
        # print(f"Created candidate ID: {data["id"]}")
        # print(data["message"])

    except requests.RequestException as e:
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")   # name of Election or Candidate

    # create new election
    parser.add_argument("-make", action="store_true")
    parser.add_argument("--target-size", type=int)
    parser.add_argument("--apply-to-all", action="store_true")

    # register new candidate
    parser.add_argument("-new-candidate", action="store_true")
    parser.add_argument("--election", type=str)
    parser.add_argument("--election-id", type=str)

    args = parser.parse_args()

    if args.make: 
        create_election(args.name, args.target_size, args.apply_to_all)

    elif args.new_candidate: 
        add_new_candidate(args.name, args.election, args.election_id)