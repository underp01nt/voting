import pandas as pd
import numpy as np
from votingutils import pairwise_comparison, pairwise_margins, weighted_pairwise_comparison, generate_random_approval_votes, generate_random_approval_disapproval_votes, generate_random_partition_votes
from ranked_pairs import topological_sort
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
    start = time.perf_counter()
    pairs = pairwise_comparison(alternatives, votes)
    # print(pairs)
    
    # Group pairs based on beat strength
    grouped_pairs = {} # strength:[edges]
    for tup,val in pairs.items():
        grouped_pairs.setdefault(val,[]).append(tup)
    
    vertices = {} # vertex:root
    edges = set() # (root1, root2)
    
    end = time.perf_counter()
    print(f"Initialization: {end - start:.6f} s")
    
    for s in sorted(grouped_pairs.keys(), reverse=True):
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

def ranked_partitions_with_margins(alternatives:list, votes:list[list]) -> list[set]:
    pairs = pairwise_comparison(alternatives, votes)
    for a,b in pairs.keys():
        pairs[(a,b)] += (pairs[(a,b)]-pairs[(b,a)])
    # Group pairs based on beat strength
    grouped_pairs = {} # strength:[edges]
    for tup,val in pairs.items():
        grouped_pairs.setdefault(val,[]).append(tup)
    
    vertices = {} # vertex:root
    edges = set() # (root1, root2)
    
    for s in sorted(grouped_pairs.keys(), reverse=True):
        if s < 0:
            continue
        print(f"{s}: {len(set(vertices.values()))} roots,    {len(edges)} edges,    {len(grouped_pairs[s])} new edges")
        
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

# alternatives = list(range(500))
# votes = generate_random_partition_votes(alternatives, 50, [0.1])
# for i, vote in enumerate(votes):
#     print(f"Vote {i}: {[len(group) for group in vote]} {">:(" if len(vote) > 2 and len(vote[len(vote)-1]) > 1.25*len(vote[0]) else ""}")
# cycles = generate_pairwise_partition(alternatives, votes)
# for j, cycle in enumerate(cycles):
#         print(f"G{j}: {len(cycle)}")
# exit()
# votes = generate_random_approval_disapproval_votes(alternatives, 5, approval_prob=0.1, disapproval_prob=0.01)
# pd.DataFrame(votes).to_csv("./data/approval_disapproval_votes.csv", index=False)
# alternatives = list(str(i) for i in range(200))
# print(pd.read_csv("./data/approval_disapproval_votes.csv").values.tolist())
# votes = [[set() if group=='set()' else set(group.strip('{}').split(', ')) for group in vote] for vote in pd.read_csv("./data/approval_disapproval_votes.csv").values.tolist()]

A = 500
V= 50
alternatives = list(range(A))
# votes = generate_random_partition_votes(alternatives, V, [10/A, 1-10/A-2/A], [0])
# votes = generate_random_partition_votes(alternatives, V, [0.01,0.02,0.05,0.915], [0])
# votes = generate_random_partition_votes(alternatives, V, [1/A]*A, [0])
votes = generate_random_partition_votes(alternatives, V, [20/A], [10/A])
target = [50,10]

# votes = [[set([0]), set([1]), set([2])], [set([2]), set([0]), set([1])], [set([1]), set([2]), set([0])]]

score = {a:0 for a in alternatives}
for vote in votes:
    scores = [1/i for i in range(1,len(vote))] + [0]
    index = 0
    for group in vote:
        for a in group:
            score[a] += scores[index]
        index += 1

# cycles = pairwise_partition(alternatives, votes)
pairs = pairwise_comparison(alternatives, votes)
wins = {(u,v):pairs[(u,v)] for u,v in pairs.keys() if pairs[(u,v)] > pairs[(v,u)]}
# cycles = ranked_partitions(alternatives, votes)

cycles = ranked_partitions(alternatives, votes)
cyclesm = ranked_paritions_with_margins(alternatives, votes)

# print(sorted(wins.values(),reverse=True))
print("Simple Condorcet:")
for cycle in pairwise_partition(alternatives, votes):
    print(f"--------------------\n{min(score[a] for a in cycle):.6f} : {cycle}")
print()

# print()
# print("Weighted Condorcet: ")
# for cycle in weighted_pairwise_partition(alternatives, votes):
#     print(f"{min(score[a] for a in cycle)} : {cycle}")

print("Ranked Partitions: ")
for cycle in cycles:
    print(f"--------------------\n{min(score[a] for a in cycle):.3f}, {len(cycle)} : {cycle}")
print()


print("Ranked Partitions w/ Margins: ")
for cycle in cyclesm:
    print(f"--------------------\n{min(score[a] for a in cycle):.3f}, {len(cycle)} : {cycle}")
print()   
# exit()

cycles = cyclesm
# for cycle in cycles:
#     print(cycle)
# print()
num_rounds = 1
vote_changes = [A-max(len(vote[i]) for i in range(len(vote))) for vote in votes]

while (num_rounds < 20):
    cycles, splits = process_partition(cycles, target)
    
    print(f"After round {num_rounds}:")
    print(f"{vote_changes} vote changes")
    for cycle in cycles:
        print(f"--------------------\n : {cycle}")
    print(splits)
    print()
    
    if len(splits) == 0:
        break
    splits.reverse()
    vote_changes = [0]*V   
    for index in splits:
        alternatives = set(cycles[index])
        n = len(alternatives)
        # print(alternatives)
        # votes_ = generate_random_partition_votes(alternatives, V, [min(5/len(alternatives),0.4),min(20/len(alternatives),0.4)], [min(5/len(alternatives),0.4),min(20/len(alternatives),0.4)])
        
        # Update preference profiles
        weights = {a:np.random.rand()*(score[a]/max(score[b] for b in alternatives)) for a in alternatives}
        for i in range(len(votes)):
            remaining = alternatives.copy()
            for group in votes[i]:
                group.difference_update(alternatives.difference(remaining))
                rem_r = np.random.rand()
                add_r = np.random.rand()
                for v in remaining:
                    if weights[v] < 0.01*rem_r:
                        group.discard(v)
                        vote_changes[i] += 1
                    elif weights[v] < 0.1*add_r:
                        group.add(v)
                        vote_changes[i] += 1
                remaining.difference_update(group)
                # print(remaining)
                # vote.append(group)
            if remaining:
                votes[i].append(remaining)

        votes_ = [[group.intersection(alternatives) for group in vote] for vote in votes]
        
        split_cycle = ranked_partitions(list(alternatives), votes_)
        cycles.pop(index)
        for cycle in reversed(split_cycle):
            cycles.insert(index, cycle)
        num_rounds += 1
        
# for cycle in cycles:
#     print(f"--------------------\n{min(score[a] for a in cycle):.6f} : {cycle}")
# print()

exit()

trials = pd.DataFrame(columns=["Trial", "Alternatives", "Votes", "Cycles"])
strata = []

for i in range(20):
    A = np.random.randint(100,501)
    V = np.random.randint(5,21)
    
    alternatives = list(range(A))
    votes = generate_random_partition_votes(alternatives, V, [1/A]*A)
    
    # votes = generate_random_partition_votes(alternatives, V, [0.05])
    # cycles = weighted_pairwise_partition(alternatives, votes)
    cycles = pairwise_partition_no_ties(alternatives, votes)
    
    trials.loc[i] = {"Trial": i+1, "Alternatives": len(alternatives), "Votes": len(votes), "Cycles": []}
    strata.append([len(cycle) for cycle in cycles])
    print(f"Trial {i+1}: {len(alternatives)}:{len(votes)} alternatives to votes")
    # print([vote[0] for vote in votes if len(vote)>1])
    # print(f"Approvals: {sum(len(vote[0]) for vote in votes)}")
    # print(f"Unique Approvals: {len(set().union(*[vote[0] for vote in votes]))}")
    for j, cycle in enumerate(cycles):
        trials.loc[i, "Cycles"].append(len(cycle))
        print(f"R{j}: {len(cycle)}")
    print()

max_row = max(len(row) for row in strata)
trial_strata = pd.DataFrame([row + [0]*(max_row - len(row)) for row in strata]).T
trial_strata['mean'] = trial_strata.replace(0,np.nan).mean(axis=1)
# trials.to_csv("./data/partitions/weighted_trials.csv", index=False)
# trial_strata.to_csv("./data/partitions/weighted_strata.csv", index=False)