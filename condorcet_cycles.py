# import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def pairwise_comparison(candidates:list, votes:list):
    pairs = {
        (a, b) : 0 for a in candidates for b in candidates if a != b
        }
    
    for vote in votes:
        for i in range(len(vote)-1):
            for j in range(i+1, len(vote)):
                pairs[(vote[i], vote[j])] += 1
                
    # return {p : pairs[p] for p in pairs if pairs[p] >= (len(votes) + 1) // 2}
    return pairs

# Returns a NetworkX graph of pairwise comparisons with edges labeled by win strength
def beat_graph(candidates:list, votes:list):
    pairs = pairwise_comparison(candidates, votes)
    pairs = {p : pairs[p] for p in pairs if pairs[p] >= (len(votes) + 1) // 2}
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([(a,b,pairs[(a,b)]) for (a,b) in pairs])
    return graph
    
if __name__ == "__main__":
    candidates = ['A', 'B', 'C']
    rankings = [['A', 'B','C']] * 24 + [['C', 'A', 'B']] * 14 + [['C', 'B', 'A']] * 12
    
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
    
    # pairs = pairwise_comparison(candidates, rankings)
    
    # print(pairs)
    
    graph = beat_graph(candidates, rankings)
    pos = nx.arf_layout(graph)
    nx.draw(graph, pos, with_labels=True)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=nx.get_edge_attributes(graph, 'weight'))
    plt.show()

