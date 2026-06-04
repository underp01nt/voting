import pandas as pd
import numpy as np
from algorithms.votingutils import pairwise_comparison, pairwise_margins, weighted_pairwise_comparison, generate_random_approval_votes, generate_random_approval_disapproval_votes, generate_random_partition_votes
from algorithms.ranked_pairs import topological_sort
import time

def get_connected_components(alternatives, pairs):
    # Kosaraju's algorithm
    unvisited = set(alt for alt in alternatives)
    L = []
    assigned = set()
    components = {}
    
    def Visit(u):
        if u in unvisited:
            unvisited.discard(u)
            for v in alternatives:
                if v in unvisited and (u,v) in pairs:
                    Visit(v)
            L.append(u)
        else:
            pass
            
    def Assign(u,root):
        if u not in assigned:
            assigned.add(u)
            components.setdefault(root,set()).add(u)
            for v in alternatives:
                if v not in assigned and (v,u) in pairs:
                    Assign(v, root)
        else:
            pass
    
    for a in alternatives:
        Visit(a)
    for a in reversed(L):
        Assign(a, a)
        
    return components

def pairwise_partition(alternatives:list, votes:list[list]):
    pairs = pairwise_comparison(alternatives, votes)
    wins = {(u,v):pairs[(u,v)] for u,v in pairs.keys() if pairs[(u,v)] >= pairs[(v,u)]}
    
    # Kosaraju's algorithm
    components = get_connected_components(alternatives, wins.keys())

    sorted_keys = sorted(components.keys(), key=lambda x : sum(pairs[(x,y)] for y in components.keys() if y != x), reverse=True)
    sorted_paritition = [components[key] for key in sorted_keys]
    
    return sorted_paritition

def weighted_pairwise_partition(alternatives:list, votes:list[list], pos_w=1, neg_w=0):
    pairs = weighted_pairwise_comparison(
        alternatives, 
        votes, 
        lambda vote: [pos_w^(2-i) for i in range(1,len(vote))] + [0],
    )
    
    wins = {(u,v):pairs[(u,v)] for u,v in pairs.keys() if pairs[(u,v)] >= pairs[(v,u)]}
    
    # Kosaraju's algorithm
    components = get_connected_components(alternatives, wins.keys())
        
    sorted_keys = sorted(components.keys(), key=lambda x : sum(pairs[(x,y)] for y in components.keys() if y != x), reverse=True)
    sorted_paritition = [components[key] for key in sorted_keys]
    
    return sorted_paritition

def pairwise_partition_no_ties(alternatives:list, votes:list[list]):
    pairs = pairwise_comparison(alternatives, votes)
    wins = {(u,v):pairs[(u,v)] for u,v in pairs.keys() if pairs[(u,v)] > pairs[(v,u)]}
    
    # Kosaraju's algorithm
    components = get_connected_components(alternatives, wins.keys())

    sorted_keys = sorted(components.keys(), key=lambda x : sum(pairs[(x,y)] for y in components.keys() if y != x), reverse=True)
    sorted_paritition = [components[key] for key in sorted_keys]
    
    return sorted_paritition

def recursive_update(v, can_reach:dict, searched:set):
    if v not in searched:    
        searched.add(v)
        for b in can_reach[v].copy():
            can_reach[v].update(recursive_update(b, can_reach, searched))
    return can_reach[v]

def ranked_partitions(alternatives:list, votes:list[list]):
    # start = time.perf_counter()
    pairs = pairwise_comparison(alternatives, votes)
    # print(pairs)
    
    # Group pairs based on beat strength
    grouped_pairs = {} # strength:[edges]
    for tup,val in pairs.items():
        grouped_pairs.setdefault(val,[]).append(tup)
    
    vertices = {} # vertex:root
    edges = set() # (root1, root2)
    
    # end = time.perf_counter()
    # print(f"Initialization: {end - start:.6f} s")
    
    for s in sorted(grouped_pairs.keys(), reverse=True):
        # print(f"{s}: {len(set(vertices.values()))} roots,    {len(edges)} edges,    {len(grouped_pairs[s])} new edges")
        
        # start_ = time.perf_counter()
        
        # Determine and store graph connections for easy access
        can_reach = {v:set() for v in vertices.values()}
        for edge in edges:
            a,b = edge
            can_reach[a].add(b)
        searched = set()
        for a in can_reach.keys():
            recursive_update(a, can_reach, searched)
        
        # Check if each pairwise win of strength s creates a cycle with stronger pairs 
        old_vertices = set(v for v in vertices.keys())
        for edge in grouped_pairs[s]:
            u, v = edge
            if u in old_vertices and v in old_vertices and vertices[u] in can_reach[vertices[v]]:
                continue
            if u not in vertices.keys():
                vertices[u] = u
            if v not in vertices.keys():
                vertices[v] = v
            edges.add((vertices[u],vertices[v]))
        
        # end = time.perf_counter()
        # print(f"    Edge addition: {end - start_:.6f} s")
        # print(f"        {topo_num} Topological Sorts: {topo_time:.6f} s")
        
        # start_ = time.perf_counter()
        
        # Collect unbreakable connected components (those with multiple edges of the same strength)
        # print(edges)
        components = get_connected_components(vertices.values(), edges)
        # print(components)
        
        # end = time.perf_counter()
        # print(f"    Connected components: {end - start_:.6f} s")
        
        # start_ = time.perf_counter()
        
        # update pointers to roots
        for root in components.keys():
            for vertex in components[root]:
                vertices[vertex] = root
        for vertex in vertices.keys():
            vertices[vertex] = vertices[vertices[vertex]]

        # update edges to match roots
        temp = set()
        for edge in edges:
            u,v = edge
            if vertices[u] != vertices[v]:
                temp.add((vertices[u], vertices[v]))
        edges = temp
        
        # end = time.perf_counter()
        # print(f"    Root/Edge updates: {end - start_:.6f} s")
        # print()
        
        # print(vertices)
        # print(edges)
        # print()
        
    # sort roots in DAG and package into list of sets
    sorted_roots, _ = topological_sort(set(vertices.values()), edges)
    # print(sorted_roots)
    output = [set(v for v in vertices if vertices[v] == root) for root in sorted_roots]
    # end = time.perf_counter()
    # print(f"Total Time: {end-start} s")
    return output

def ranked_partitions_with_margins(alternatives:list, votes:list[list]) -> list[set]:
    # Parse string and lists into sets for easier processing
    if type(votes[0][0]) == str:
        for i in range(len(votes)):
            votes[i] = [set(part.split(",")) for part in votes[i]]
    if type(votes[0][0]) == list:
        for i in range(len(votes)):
            votes[i] = [set(part) for part in votes[i]]
    
    pairs_ = pairwise_comparison(alternatives, votes)
    # pairs = pairs_.copy()
    
    pairs = {}
    num_votes = len(votes)
    for a,b in pairs_.keys():
        pairs[(a,b)] = (pairs_[(a,b)]-pairs_[(b,a)])/(2*num_votes-(pairs_[(a,b)]+pairs_[(b,a)]))
    
    # smith_set = set(a for a in alternatives if all(pairs[(a,b)] >= 0 for b in alternatives if b != a))
    # print(f"Smith Set: {smith_set}")
    
    # Group pairs based on beat strength
    grouped_pairs = {} # strength:[edges]
    for tup,val in pairs.items():
        grouped_pairs.setdefault(val,[]).append(tup)
    
    vertices = {} # vertex:root
    edges = set() # (root1, root2)
    
    for s in sorted(grouped_pairs.keys(), reverse=True):
        if s < 0:
            continue
        # print(f"{s}: {len(set(vertices.values()))} roots,    {len(edges)} edges,    {len(grouped_pairs[s])} new edges")
        
        # Determine and store graph connections for easy access
        can_reach = {v:set() for v in vertices.values()}
        for edge in edges:
            a,b = edge
            can_reach[a].add(b)
        searched = set()
        for a in can_reach.keys():
            recursive_update(a, can_reach, searched)
        
        # phase1 = can_reach.copy()
        
        # searched = set()
        # for a in can_reach.keys():
        #     recursive_update(a, can_reach, searched)
        
        # for a in can_reach.keys():
        #     if can_reach[a].difference(phase1[a]):
        #         print(f"Error: {a} can reach {can_reach[a]} but only {phase1[a]} in phase 1")
        #         print(f"Votes: {votes}")
        #         print()
                
        # Check if each pairwise win of strength s creates a cycle with stronger pairs 
        old_vertices = set(v for v in vertices.keys())
        for edge in grouped_pairs[s]:
            u, v = edge
            if u in old_vertices and v in old_vertices and vertices[u] in can_reach[vertices[v]]:
                continue
            if u not in vertices.keys():
                vertices[u] = u
            if v not in vertices.keys():
                vertices[v] = v
            edges.add((vertices[u],vertices[v]))
        
        # Collect unbreakable connected components (those with multiple edges of the same strength)
        components = get_connected_components(vertices.values(), edges)
        
        # update pointers to roots
        for root in components.keys():
            for vertex in components[root]:
                vertices[vertex] = root
        for vertex in vertices.keys():
            vertices[vertex] = vertices[vertices[vertex]]

        # update edges to match roots
        temp = set()
        for edge in edges:
            u,v = edge
            if vertices[u] != vertices[v]:
                temp.add((vertices[u], vertices[v]))
        edges = temp
        
    # sort roots in DAG and package into list of sets
    sorted_roots, _ = topological_sort(set(vertices.values()), edges)
    # print(sorted_roots)
    output = [set(v for v in vertices if vertices[v] == root) for root in sorted_roots]
    return output


def timed_ranked_partitions_with_margins(alternatives:list, votes:list[list]) -> list[set]:
    start = time.perf_counter()
    # pairs = pairwise_margins(alternatives, votes)
    # print(pairs)
    
    pairs = pairwise_comparison(alternatives, votes)
    for a,b in pairs.keys():
        pairs[(a,b)] += (pairs[(a,b)]-pairs[(b,a)])
    # Group pairs based on beat strength
    grouped_pairs = {} # strength:[edges]
    for tup,val in pairs.items():
        grouped_pairs.setdefault(val,[]).append(tup)
    
    vertices = {} # vertex:root
    edges = set() # (root1, root2)
    
    end = time.perf_counter()
    print(f"Initialization: {end - start:.6f} s")
    
    for s in sorted(grouped_pairs.keys(), reverse=True):
        if s < 0:
            continue
        print(f"{s}: {len(set(vertices.values()))} roots,    {len(edges)} edges,    {len(grouped_pairs[s])} new edges")
        
        start_ = time.perf_counter()
        
        # Determine and store graph connections for easy access
        can_reach = {v:set() for v in vertices.values()}
        for edge in edges:
            a,b = edge
            can_reach[a].add(b)
        searched = set()
        for a in can_reach.keys():
            recursive_update(a, can_reach, searched)
        
        # Check if each pairwise win of strength s creates a cycle with stronger pairs 
        old_vertices = set(v for v in vertices.keys())
        for edge in grouped_pairs[s]:
            u, v = edge
            if u in old_vertices and v in old_vertices and vertices[u] in can_reach[vertices[v]]:
                continue
            if u not in vertices.keys():
                vertices[u] = u
            if v not in vertices.keys():
                vertices[v] = v
            edges.add((vertices[u],vertices[v]))
        
        end = time.perf_counter()
        print(f"    Edge addition: {end - start_:.6f} s")
        # print(f"        {topo_num} Topological Sorts: {topo_time:.6f} s")
        
        start_ = time.perf_counter()
        
        # Collect unbreakable connected components (those with multiple edges of the same strength)
        # print(edges)
        components = get_connected_components(vertices.values(), edges)
        # print(components)
        
        end = time.perf_counter()
        print(f"    Connected components: {end - start_:.6f} s")
        
        start_ = time.perf_counter()
        
        # update pointers to roots
        for root in components.keys():
            for vertex in components[root]:
                vertices[vertex] = root
        for vertex in vertices.keys():
            vertices[vertex] = vertices[vertices[vertex]]

        # update edges to match roots
        temp = set()
        for edge in edges:
            u,v = edge
            if vertices[u] != vertices[v]:
                temp.add((vertices[u], vertices[v]))
        edges = temp
        
        end = time.perf_counter()
        print(f"    Root/Edge updates: {end - start_:.6f} s")
        print()
        
        # print(vertices)
        # print(edges)
        # print()
        
    # sort roots in DAG and package into list of sets
    sorted_roots, _ = topological_sort(set(vertices.values()), edges)
    # print(sorted_roots)
    output = [set(v for v in vertices if vertices[v] == root) for root in sorted_roots]
    end = time.perf_counter()
    print(f"Total Time: {end-start} s")
    return output

def greedy_partitions(alternatives:list, votes:list[list]):
    
    pass

def process_partition(partition:list[set], targets:list[int]) -> tuple[list[set], list[int]]:
    diff = sum(len(part) for part in partition) - sum(targets)
    if diff > 0:
        targets.append(diff)
    optimized = []
    split_indices = []
    index = 1
    target = targets[0]
    append_bool = True
    for group in partition:
        target -= len(group)
        if target < 0:
            # print("append")
            split_indices.append(len(optimized))
            optimized.append(group)
            # append_bool = True
        elif append_bool:
            # print("append")
            optimized.append(group)
            append_bool = False
        else:
            # print("union")
            optimized[-1] = optimized[-1].union(group)
        # if target == 0:
        while target <= 0 and index < len(targets):
            append_bool = True
            target += targets[index]
            index += 1
    return optimized, split_indices

# def process_tagged_partition(partition:list[set], tags:list[dict[str,int]], targets:list[dict[str,int]]):
#     for i in range(len(partition)):
#         part = partition[i]
#         tag = tags[i]
        
#         target["len"] -= len(part)
#         bad = target["len"] < 0
#         for key in target.keys():
#             target[key] -= tag[key]
#             if target[key] <= 0:
#                 append_bool = True
#             bad |= target[key] < 0
#         if bad:
#             # print("append")
#             split_indices.append(len(optimized))
#             optimized.append(part)
#             optimized_tags.append(tag)
#         elif append_bool:
#             # print("append")
#             optimized.append(part)
#             optimized_tags.append(tag)
#             append_bool = False
#         else:
#             # print("union")
#             optimized[-1] = optimized[-1].union(part)
#             optimized_tags[-1].update({key:val+tag[key] for key,val in optimized_tags[-1].items() if key in tag.keys()})
#         over = target["len"] <= 0
#         for key in target.keys():
#             over |= target[key] <= 0
#         while over and index < len(targets):
#             over = target["len"] <= 0
#         for key in target.keys():
#             over |= target[key] <= 0
#         target["len"] <= 0 and len(targets) > :
#             target["len"] += targets[index]["len"]
#         for key in target.keys():
#             while
            
#     return optimized, optimized_tags, split_indices

if __name__ == "__main__":
    # for _ in range(20):
        # alts = list(range(20))
        
    # from algorithms.votingutils import generate_random_votes
    # votes = generate_random_votes(alts, 10)
    # print(votes)
    
    partition = ranked_partitions_with_margins(
        ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        [
            ['1', '4', '2', '7', '0', '6', '5', '8', '3', '9'],
            ['4', '7', '9', '5', '6', '1', '3', '0', '8', '2'],
            ['6', '4', '3', '2', '5', '8', '7', '0', '9', '1'],
            ['2', '3', '6', '1', '4', '8', '5', '9', '0', '7'],
            ['1', '7', '0', '2', '9', '8', '4', '6', '3', '5'],
            ['5', '1', '2', '3', '8', '9', '7', '6', '0', '4'],
            ['1', '6', '3', '9', '0', '4', '8', '7', '2', '5'],
            ['1', '4', '8', '7', '6', '2', '3', '9', '5', '0'],
            ['5', '6', '0', '3', '9', '4', '1', '2', '8', '7'],
            ['4', '0', '9', '3', '7', '2', '5', '6', '1', '8']
        ]
    )
    print(partition)