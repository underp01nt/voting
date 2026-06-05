import numpy as np
import pandas as pd
from algorithms.votingutils import pairwise_margins, matrix_of_majorities

# Basically a topological sort of the DAG, except it might not be
# connected and what even are vertices?
def topological_sort(vertices:list, edges:list):
    if not vertices:
        return vertices, edges
    
    indegrees = {v: 0 for v in vertices}
    for edge in edges:
        indegrees[edge[1]] += 1
    
    start = [v for v in vertices if indegrees[v] == 0]
    if not start:
        raise Warning("Full Cycle")
    
    final = []
    remaining_edges = edges.copy()
    while start:
        node = start.pop()
        final.append(node)
        for edge in remaining_edges.copy():
            if edge[0] == node:
                remaining_edges.remove(edge)
                indegrees[edge[1]] -= 1
                if indegrees[edge[1]] == 0:
                    start.insert(0, edge[1])
        # print(indegrees)
    
    if len(final) < len(vertices):
        raise Warning("Embedded Cycle")
                
    return final, edges

def ranked_pairs(candidates:list, votes:list) -> list:
    pairs = pairwise_margins(candidates, votes)
    sorted_pairs = sorted((pair for pair,margin in pairs.items() if margin>=0), key=lambda x: (pairs[x], np.random.rand()), reverse=True)
    # sorted_wins = sorted_pairs[:len(sorted_pairs)//2]
    sorted_wins = sorted_pairs
    
    vertices = []
    edges = []
    i = 0
    while i < len(sorted_wins):
        try:
            vertices, edges = topological_sort(
                vertices + [v for v in sorted_wins[i] if v not in vertices],
                edges + [sorted_wins[i]]
            )
        except Warning as e:
            # print(e)
            pass
        finally:
            i += 1
    return vertices

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
    
    candidates = ['A', 'B', 'C']
    rankings = [['A', 'B','C']] * 24 + [['C', 'A', 'B']] * 14 + [['C', 'B', 'A']] * 12
    
    ranking = ranked_pairs(candidates, rankings)
    
    print(ranking)


def ranked_pairs_numerical(candidates:list, votes:list):
    matrix, _ = matrix_of_majorities(candidates, votes)
    pass