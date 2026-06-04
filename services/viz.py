from plotly import graph_objects as go

def build_heat_map(candidates: list[str], ballots: list[list[str]], candidate_map=None) -> go.Figure:
    pairs = {a: {b: 0 for b in candidates} for a in candidates}
    name_lookup = {c["candidate_id"]: c["name"] for c in candidate_map}
    labels = [name_lookup.get(candidate_id, candidate_id) for candidate_id in candidates]

    # track tier-aware beats 
    for ballot in ballots:
        for higher_tier_index in range(len(ballot)):
            for lower_tier_index in range(higher_tier_index + 1, len(ballot)):
                for a in ballot[higher_tier_index]:
                    for b in ballot[lower_tier_index]:
                        pairs[a][b] += 1

    # build matrix based on pairwise match-up scores
    mat = [[pairs[a][b] for b in candidates] for a in candidates]

    heat = go.Figure(data=go.Heatmap(z=mat, x=labels, y=labels, colorscale="Blues", zmin=0))
    heat.update_layout(
        title={"text": "Pairwise Comparisons (Vertical vs. Horizontal)", "x": 0.5}, 
        yaxis=dict(scaleanchor="x"), width=500, height=500,
    )
    return heat

def build_rank_table(ranking: list[set]) -> go.Figure:
    num_parts = len(ranking)
    rank_indices = list(range(1, num_parts + 1))

    # Claude's fix for ranking parsing, plotly...
    display_ranking = [", ".join(sorted(group)) for group in ranking]

    fig = go.Figure(data=go.Table(
        header=dict(values=["Rank", "Candidate"]),
        cells=dict(values=[list(rank_indices), display_ranking])
    ))

    fig.update_layout(title={"text": "Final Ranking", "x": 0.5}, height=max(300, 200 + num_parts * 40))
    return fig