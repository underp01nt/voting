from ranked_pairs import ranked_pairs
from services.viz import build_rank_table, build_heat_map
from services.utils import generate_id
from io import StringIO
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

def insert_or_get_ballot(db, hashed_signature: str, encrypted_ballot=None):
    cursor = db.cursor()

    cursor.execute(
        """
            INSERT INTO ballots (hashed_signature, encrypted_ballot)
            VALUES (%s, %s)
            ON CONFLICT (hashed_signature) DO NOTHING
        """,
        (hashed_signature, encrypted_ballot)
    )

    db.commit()

def create_new_election(db, **kwargs):
    cursor = db.cursor()

    try:
        query = """
            INSERT INTO elections (id, name, target_size, valid, round)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """

        valid=True; id=generate_id(16); round=1
        data = (id, kwargs["name"], kwargs["target_size"], valid, round)

        cursor.execute(query, data)
        result = cursor.fetchone()

        if not result: raise Exception("New election insertion failed") 
        else: election_id = result[0]

        # register all voters to this election if specified
        if kwargs.get("apply_to_all"):
            update_query = """
                UPDATE ballots
                SET election_id = %s, round = %s
            """

            cursor.execute(update_query, (election_id, round))

        db.commit()
        return election_id

    except Exception:
        db.rollback()
        raise