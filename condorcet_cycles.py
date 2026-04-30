import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# candidates: array of candidate names, 
# votes: array of rankings (arrays of candidate names in order of preference)
# returns a dict of *all* pairwise (order dependent) vote totals
def pairwise_comparison(candidates:list, votes:list):
    pairs = {
        (a, b) : 0 for a in candidates for b in candidates if a != b
        }
    
    for vote in votes:
        for i in range(len(vote)-1):
            for j in range(i+1, len(vote)):
                pairs[(vote[i], vote[j])] += 1
                
    return pairs

# Returns a NetworkX graph of pairwise comparisons with edges labeled by win strength
def beat_graph(candidates:list, votes:list):
    pairs = pairwise_comparison(candidates, votes)
    pairs = {p : pairs[p] for p in pairs if pairs[p] >= (len(votes) + 1) // 2}
    
    graph = nx.DiGraph()
    graph.add_nodes_from(candidates)
    graph.add_weighted_edges_from([(a,b,pairs[(a,b)]) for (a,b) in pairs], weight='strength')
    return graph

# draws the graph of pairwise victories with matplotlib
def draw_beat_graph(candidates:list, votes:list):
    graph = beat_graph(candidates, votes)
    # indegrees = {c : 0 for c in candidates}
    # for edge in graph.edges:
    #     indegrees[edge[1]] += 1
    # for node in graph.nodes:
    #     graph.nodes[node]['indegree'] = indegrees[node]
    # pos = nx.multipartite_layout(graph, subset_key='indegree')
    pos = nx.circular_layout(graph)
    nx.draw(
        graph, 
        pos, 
        with_labels=True, 
        node_color=['C' + str(i%10) for i in range(len(candidates))],
        width=1.5,
        arrowsize=50,
        node_size=2000,
        font_size=30,
        # connectionstyle='arc3, rad = 0.1'
        )
    nx.draw_networkx_edge_labels(
        graph, 
        pos, 
        edge_labels=nx.get_edge_attributes(graph, 'strength'), 
        label_pos=0.25, 
        font_size=20,
        rotate=False
        # connectionstyle='arc3, rad = 0.1'
        )
    
if __name__ == "__main__":
    candidates = ['A', 'B', 'C', 'D']
    rankings = [
        ['A', 'B', 'C', 'D'],
        ['A', 'B', 'C', 'D'],
        ['A', 'B', 'D', 'C'],
        ['B', 'A', 'C', 'D'],
        ['C', 'D', 'A', 'B'],
        ['C', 'D', 'A', 'B'],
        ['C', 'D', 'A', 'B'],
        ['C', 'D', 'B', 'A'],
        ['D', 'C', 'B', 'A'],
        ['D', 'C', 'B', 'A'],
    ]
    
    from votingutils import generate_random_votes
    rankings = generate_random_votes(candidates, 50)
    
    # candidates = ['A', 'B', 'C']
    # rankings = [['A', 'B','C']] * 48 + [['C', 'A', 'B']] * 28 + [['C', 'B', 'A']] * 24
    
    # pairs = pairwise_comparison(candidates, rankings)
    
    # print(pairs)
    
    # candidates = ['A', 'B', 'C']
    # rankings = [['A', 'C','B']] * 40 + [['B', 'C', 'A']] * 30 + [['B', 'A', 'C']] * 30
    
    draw_beat_graph(candidates, rankings)
    plt.show()

