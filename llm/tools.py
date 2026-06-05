from admin.manage import create_election, add_new_candidate, nominate_candidate

def process_election(election_name: str, candidates: list[str], target_size: list[int]):
    election = create_election(election_name, str(target_size))

    for candidate in candidates:
        candidate = add_new_candidate(candidate)
        nominate_candidate(candidate["id"], election["id"])