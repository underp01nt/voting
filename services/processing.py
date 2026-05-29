from ranked_pairs import ranked_pairs
from services.viz import build_rank_table, build_heat_map
from services.utils import generate_id
from io import StringIO
from typing import Optional
import time,csv

# convert data to text, then make text reader iterable per row
def parse_csv(data: bytes) -> list[list[str]]:
    text: str = data.decode("utf-8")  # convert file content to text
    reader = csv.reader(StringIO(text))
    return [row for row in reader if row]

# count all votes using ranked_pairs, returns results dict for template context
def count_votes(candidates: list[str], ballots: list[list[str]]) -> dict:
    results = {}

    start = time.time()
    ranked_pairs_result = ranked_pairs(candidates, ballots)
    end = time.time()

    fig = build_rank_table(ranked_pairs_result)
    heat = build_heat_map(candidates, ballots)

    results["Ranked pairs"] = {
        "duration": end - start,
        "fig": fig.to_html(full_html=False, config={"responsive": True}),
        "heat": heat.to_html(full_html=False, config={"responsive": True})
    }

    return results

def insert_or_get_voter(db, hashed_signature: str):
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO voters (hashed_signature)
        VALUES (%s)
        ON CONFLICT (hashed_signature) DO NOTHING
        """,
        (hashed_signature,)
    )

    db.commit()

def insert_or_get_ballot(db, hashed_signature: str, encrypted_ballot=None, election_id=None):
    cursor = db.cursor()

    cursor.execute(
        """
            INSERT INTO ballots (hashed_signature, encrypted_ballot, election_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (hashed_signature, election_id) DO NOTHING
        """,
        (hashed_signature, encrypted_ballot, election_id)
    )

    db.commit()

# returns election ID if election is successfully created
def create_new_election(db, name: str, target_size: int, apply_to_all: bool) -> str:
    cursor = db.cursor()

    try:
        query = """
            INSERT INTO elections (id, name, target_size, valid, round)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """

        valid=True; id=generate_id(16); round_number=1
        data = (id, name, target_size, valid, round_number)

        cursor.execute(query, data)
        result = cursor.fetchone()

        if not result: raise Exception("New election insertion failed") 
        else: election_id = result[0]

        # register all voters to this election if specified
        if apply_to_all:
            update_query = """
                UPDATE ballots
                SET election_id = %s, round = %s
            """

            cursor.execute(update_query, (election_id, round_number))

        db.commit()
        return election_id

    except Exception:
        db.rollback()
        raise

# returns candidate ID if candidate is successfully created
def add_new_candidate(name: str, election_name: Optional[str], election_id: Optional[str], db) -> str: 
    cursor = db.cursor()

    try:
        if not election_id and election_name:  # make query to elections table to find the election
            cursor.execute("SELECT id FROM elections WHERE name = %s", (election_name,))
            result = cursor.fetchone()

            if not result: 
                raise ValueError(f"Could not find election with name {election_name}")
            
            election_id = result[0]

        query = """
            INSERT INTO candidates (id, name, election_id)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        candidate_id = generate_id(8)
        data = (candidate_id, name, election_id)
        
        cursor.execute(query, data)
        db.commit()

        return candidate_id

    except Exception:
        db.rollback()
        raise