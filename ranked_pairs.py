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
        raise Exception("Cycle")
    
    final = []
    remaining_edges = edges.copy()
    while start:
        node = start.pop()
        final.append(node)
        for edge in remaining_edges:
            if edge[0] == node:
                remaining_edges.remove(edge)
                indegrees[edge[1]] -= 1
                if indegrees[edge[1]] == 0:
                    start.insert(0, edge[1])
    
    if len(remaining_edges) > 0:
        raise Exception("Embedded Cycle")
    
    print(final)
                
    return final, edges

def ranked_pairs(candidates, votes):
    pairs = {
        (a, b) : 0 for a in candidates for b in candidates if a != b
        }
    
    for vote in votes:
        for i in range(len(vote)-1):
            for j in range(i+1, len(vote)):
                pairs[(vote[i], vote[j])] += 1
    
    sorted_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)
    sorted_pairs = sorted_pairs[:len(sorted_pairs)//2]
    
    print(sorted_pairs)
    
    vertices = []
    edges = []
    i = 0
    while len(edges) < len(candidates)-1:
        if (i >= len(sorted_pairs)):
            raise Exception("No winner?")
        try:
            vertices, edges = topological_sort(
                vertices + [v for v in sorted_pairs[i][0] if v not in vertices],
                edges + [sorted_pairs[i][0]]
            )
        except Exception:
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
    
    ranking = ranked_pairs(candidates, rankings)
    
    print(ranking)
