from collections import Counter
from algorithms.partitions import ranked_partitions_with_margins, process_partition
from services.crypto import aesgcm, aes_encrypt, aes_decrypt
from services.viz import build_rank_table, build_heat_map
from services.utils import generate_id
from io import StringIO
from typing import Optional
import csv, time, json

# convert data to text, then make text reader iterable per row
def parse_csv(data: bytes) -> list[list[str]]:
    text: str = data.decode("utf-8")  # convert file content to text
    reader = csv.reader(StringIO(text))
    return [row for row in reader if row]

# count all votes using ranked_pairs, returns results dict for template context
def count_votes(candidates: list[str], ballots: list[list[str]]) -> dict:
    results = {}
    
    start = time.time()
    ranked_partitions_result = ranked_partitions_with_margins(candidates, ballots)
    
    target = None #NEED TARGET

    processed_partition, split_indices = process_partition(ranked_partitions_result, target)
    end = time.time()
    
    fig = build_rank_table(processed_partition)
    heat = build_heat_map(candidates, ballots)

    results["Partition"] = {
        "duration": end - start,
        "fig": fig.to_html(full_html=False, config={"responsive": True}),
        "heat": heat.to_html(full_html=False, config={"responsive": True})
    }
    
    results["Next Round"] = {
        "to_split": split_indices[0] if split_indices else None
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

# creates and saves voter ballot submission
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

def process_targets(targets: list[int], num_candidates: int) -> list[int]:
    diff = num_candidates - sum(targets)
    return targets.append(diff) if diff > 0 else targets

# returns election ID if election is successfully created
def create_new_election(db, name: str, target_size: list[int]) -> str:
    cursor = db.cursor()

    try:
        make_new_election_query = """
            INSERT INTO elections (id, name, target_size, valid, round)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """

        valid=True; election_id=generate_id(5); round_number=1
        data = (election_id, name, target_size, valid, round_number)

        cursor.execute(make_new_election_query, data)
        result = cursor.fetchone()

        if not result: raise Exception("New election insertion failed") 
        else: 
            db.commit(); return election_id

    except Exception:
        db.rollback()
        raise

# returns candidate ID if candidate is successfully created
def add_new_candidate(name: str, db) -> str: 
    cursor = db.cursor()

    try:
        add_new_candidate_query = """
            INSERT INTO candidates (id, name)
            VALUES (%s, %s)
            RETURNING id
        """
        candidate_id = generate_id(8)
        data = (candidate_id, name)
        cursor.execute(add_new_candidate_query, data)

        result = cursor.fetchone()

        if not result: raise Exception("New candidate insertion failed") 
        else: 
            db.commit(); return candidate_id

    except Exception:
        db.rollback()
        raise

# returns list of a voter's elections (+ metadata) 
def get_elections(hashed_signature: str, db) -> list[dict]: 
    cursor = db.cursor()

    try:
        active_elections_query = \
            """
                SELECT e.id, e.name, e.round, e.created_at, (
                    SELECT COUNT(*)
                    FROM election_candidates ec
                    WHERE ec.election_id = e.id
                ), b.last_updated
                FROM ballots b
                JOIN elections e ON b.election_id = e.id
                WHERE hashed_signature = %s AND e.valid = TRUE
                ORDER BY e.created_at DESC
            """
        data = (hashed_signature,) 
        cursor.execute(active_elections_query, data)

        return [{
            "id": row[0], 
            "name": row[1], 
            "round": row[2],
            "created_at": row[3],
            "count": row[4],
            "last_updated": row[5]
        } for row in cursor.fetchall()]

    except Exception:
        raise

def register_voter_to_election(hashed_signature, election_id, db) -> str:
    cursor = db.cursor()

    try:
        register_voter_query = \
            """
            INSERT INTO ballots (id, hashed_signature, election_id)
            VALUES (%s, %s, %s)
            RETURNING id
            """
        ballot_id = generate_id(6)
        data = (ballot_id, hashed_signature, election_id)
        cursor.execute(register_voter_query, data)

        result = cursor.fetchone()

        if not result:
            raise Exception("Failed to register new ballot in DB")
         
        else:
            db.commit(); return ballot_id

    except Exception:
        db.rollback()
        raise

# nominates a candidate for a specific election
def nominate_candidate(db, candidate_id: str, election_id: str) -> dict[str, str]:
    try:
        cursor = db.cursor()
        nominate_query = \
            """
                INSERT INTO election_candidates (election_id, candidate_id)
                VALUES (%s, %s)
                RETURNING election_id, candidate_id
            """
        cursor.execute(nominate_query, (election_id, candidate_id))
        row = cursor.fetchone()

        if row is None: raise ValueError("Nomination was not created")
        else: db.commit()

        return {"election_id": row[0], "candidate_id": row[1]}

    except Exception:
        db.rollback()
        raise

def check_voter_in_election(hashed_signature: str, election_id: str, db) -> Optional[tuple]:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT 1
        FROM ballots
        WHERE hashed_signature = %s
        AND election_id = %s
        """,
        (hashed_signature, election_id)
    )
    return cursor.fetchone()

# returns list of name and id mappings
def get_candidates(election_id: str, db) -> list[dict]:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT c.name, c.id 
        FROM candidates c
        JOIN election_candidates ec on c.id = ec.candidate_id
        JOIN elections e on ec.election_id = e.id
        WHERE e.id = %s AND (ec.round_eliminated IS NULL)
        """,
        (election_id,)
    )
    return [{"name": row[0], "candidate_id": row[1]} for row in cursor.fetchall()]

def get_existing_ballot(hashed_signature, election_id, db):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT e.name, b.id, b.encrypted_ballot, b.last_updated, e.round
        FROM ballots b
        JOIN elections e on e.id = b.election_id
        WHERE hashed_signature = %s AND election_id = %s
        """, 
        (hashed_signature, election_id)
    )
    return cursor.fetchone()

def submit_ballot(hashed_signature: str, election_id: str, candidate_ids: list[str], round_number: int, db):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
                UPDATE ballots
                SET encrypted_ballot = %s, last_updated = NOW(), round = %s
                WHERE hashed_signature = %s AND election_id = %s
            """,
            (aes_encrypt(aesgcm, json.dumps(candidate_ids)), round_number, hashed_signature, election_id)
        ); db.commit()
    
    except Exception:
        db.rollback()
        raise

def has_submitted_ballot(hashed_signature: str, election_id: str, db) -> bool:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT 1
        FROM ballots
        WHERE hashed_signature = %s AND election_id = %s AND encrypted_ballot IS NOT NULL
        """,
        (hashed_signature, election_id)
    )
    return cursor.fetchone() is not None

def get_standings(election_id: str, round_number: int, db) -> list[dict]:
    try:
        cursor = db.cursor()
        # get ballots for the election at the current round
        cursor.execute(
            """
                SELECT b.encrypted_ballot
                FROM ballots b
                WHERE election_id = %s AND round = %s AND encrypted_ballot IS NOT NULL
            """,
            (election_id, round_number)
        )

        encrypted_ballots = cursor.fetchall()

        match round_number:
            case 1: 
                counts = Counter()
                for (encrypted_ballot,) in encrypted_ballots:
                    candidate_ids = json.loads(aes_decrypt(aesgcm, encrypted_ballot))
                    for candidate_id in candidate_ids:
                        counts[candidate_id] += 1

                candidate_lookup = {c["candidate_id"]: c["name"] for c in get_candidates(election_id, db)}
                standings = [{
                                "name": candidate_lookup[candidate_id],
                                "candidate_id": candidate_id,
                                "num_approvals": num_approvals, 
                             }
                            for candidate_id, num_approvals in counts.items()]
                standings.sort(key=lambda x: x["num_approvals"], reverse=True)
                # print(counts); print(standings)

                return standings

            case _: raise Exception("Round not yet implemented")  # TODO: work on multiple round
    except Exception: raise
