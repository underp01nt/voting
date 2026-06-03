from admin.manage import create_election, add_new_candidate, nominate_candidate

def process_election(election_name: str, candidates: list[str], target_size: int):
    election = create_election(election_name, target_size)
    # TODO: assign election to voters

    for candidate in candidates:
        candidate = add_new_candidate(candidate)
        nominate_candidate(candidate["id"], election["id"])