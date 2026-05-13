from ranked_pairs import ranked_pairs
from services.viz import build_rank_table, build_heat_map
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