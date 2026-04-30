import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from votingutils import generate_random_votes, pairwise_comparison

# Returns a NetworkX graph of pairwise comparisons with edges labeled by win strength
def beat_graph(candidates:list, votes:list):
    pairs = pairwise_comparison(candidates, votes)
    pairs = {p : pairs[p] for p in pairs if pairs[p] >= (len(votes) + 1) // 2}
    
    graph = nx.DiGraph()
    graph.add_nodes_from(candidates)
    graph.add_weighted_edges_from([(a,b,pairs[(a,b)]) for (a,b) in pairs], weight='strength')
    return graph

# draws the graph of pairwise victories with matplotlib
def draw_beat_graph(candidates:list, votes:list, display=False, block=True):
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
    if display:
        plt.show(block=block)
    
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
    
    rankings = generate_random_votes(candidates, 50)
    
    # candidates = ['A', 'B', 'C']
    # rankings = [['A', 'B','C']] * 48 + [['C', 'A', 'B']] * 28 + [['C', 'B', 'A']] * 24
    
    # pairs = pairwise_comparison(candidates, rankings)
    
    # print(pairs)
    
    # candidates = ['A', 'B', 'C']
    # rankings = [['A', 'C','B']] * 40 + [['B', 'C', 'A']] * 30 + [['B', 'A', 'C']] * 30
    
    # draw_beat_graph(candidates, rankings)
    
    # candidates_1 = ['A', 'B', 'C']
    # rankings_1 = [['A', 'B','C']] * 52 + [['C', 'B', 'A']] * 48
    
    candidates_2 = ['A', 'B', 'C', 'b']
    rankings_2 = [['A', 'B', 'b', 'C']] * 26 + [['A', 'b', 'B', 'C']] * 26 + [['C', 'B', 'b', 'A']] * 24 + [['C', 'b', 'B', 'A']] * 24

    # draw_beat_graph(candidates_1, rankings_1)
    draw_beat_graph(candidates_2, rankings_2)
    
    plt.show()

