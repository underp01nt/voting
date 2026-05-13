from plotly import graph_objects as go

def build_heat_map(candidates: list[str], ballots: list[list[str]]) -> go.Figure:
    pairs = {a: {b: 0 for b in candidates} for a in candidates}
    for ballot in ballots:
        for i in range(len(ballot)):  #  i > j, get number of voters preferred (or after) candidate i
            for j in range(i + 1, len(ballot)):
                pairs[ballot[i]][ballot[j]] += 1

    # build matrix based on pairwise match-up scores
    mat = [[pairs[a][b] for b in candidates] for a in candidates]

    heat = go.Figure(data=go.Heatmap(z=mat, x=candidates, y=candidates, colorscale="Blues", zmin=0))
    heat.update_layout(
        title={"text": "Pairwise Comparisons (Vertical vs. Horizontal)", "x": 0.5}, 
        yaxis=dict(scaleanchor="x"), width=500, height=500,
    )
    return heat

def build_rank_table(ranking: list[str]) -> go.Figure:
    num_candidates = len(ranking)
    rank_indices = list(range(1, num_candidates + 1))
    fig = go.Figure(data=go.Table(
        header=dict(values=["Rank", "Candidate"]),
        cells=dict(values=[rank_indices, ranking])
    ))

    fig.update_layout(title={"text": "Final Ranking", "x": 0.5}, height=180 + num_candidates * 30)
    return fig