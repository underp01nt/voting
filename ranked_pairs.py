import numpy as np
import pandas as pd
from votingutils import pairwise_comparison

# Basically a topological sort of the DAG, except it might not be
# connected and what even are vertices?
def topological_sort(vertices:list, edges:list):
    indegrees = {v: 0 for v in vertices}
    for edge in edges:
        indegrees[edge[1]] += 1
    
    start = [v for v in vertices if indegrees[v] == 0]
    if not start:
        raise Exception("Full Cycle")
    
    final_vertices = []
    final_edges =[]
    remaining_edges = edges.copy()
    while start:
        node = start.pop()
        final_vertices.append(node)
        for edge in remaining_edges.copy():
            if edge[0] == node:
                final_edges.append(edge)
                remaining_edges.remove(edge)
                indegrees[edge[1]] -= 1
                if indegrees[edge[1]] == 0:
                    start.insert(0, edge[1])
        # print(indegrees)
    
    if len(final_vertices) < len(vertices):
        raise Exception("Embedded Cycle")
                
    return final_vertices, final_edges

def ranked_pairs(candidates:list, votes:list):
    pairs = pairwise_comparison(candidates, votes)
    
    sorted_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)
    sorted_wins = sorted_pairs[:len(sorted_pairs)//2]
    
    vertices = []
    edges = []
    i = 0
    while i < len(sorted_wins):
        try:
            vertices, edges = topological_sort(
                vertices + [v for v in sorted_wins[i][0] if v not in vertices],
                edges + [sorted_wins[i][0]]
            )
        except Exception as e:
            print(e)
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
