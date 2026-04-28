import numpy as np
import pandas as pd
from rankings import generate_random_votes

# Basically a topological sort of the DAG, except it might not be
# connected and what even are vertices?
def topological_sort(vertices:list, edges:list):
    indegrees = {v: 0 for v in vertices}
    for edge in edges:
        indegrees[edge[1]] += 1
    
    start = [v for v in vertices if indegrees[v] == 0]
    if not start:
        raise Exception("Full Cycle")
    
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
        raise Exception("Embedded Cycle")
                
    return final, edges

def ranked_pairs(candidates:list, votes:list):
    pairs = {
        (a, b) : 0 for a in candidates for b in candidates if a != b
        }
    
    for vote in votes:
        for i in range(len(vote)-1):
            for j in range(i+1, len(vote)):
                pairs[(vote[i], vote[j])] += 1
    
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
