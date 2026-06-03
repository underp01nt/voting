from algorithms.partitions import *
from algorithms.ranked_pairs import ranked_pairs
from algorithms.votingutils import *

NUM_TESTS = 1000

def ranked_pairs_ranked_partitions_equivalence(minA=1, maxA=20, minV=1, maxV=20, verbose=False):
    passed = 0
    for i in range(NUM_TESTS):
        A = np.random.randint(minA, maxA+1)
        V = np.random.randint(minV, maxV+1)
        candidates = list(str(i) for i in range(A))
        votes = generate_random_votes(candidates, V)
        rp_result = ranked_pairs(candidates, votes)
        rparts_result = ranked_partitions_with_margins(candidates, votes)
        
        # Smith set calculation
        margins = pairwise_margins(candidates, votes)
        wins = {c:0 for c in candidates}
        for tup,val in margins.items():
            if val > 0:
                wins[tup[0]] += 1.0
            if val == 0:
                wins[tup[0]] += 0.5
        max_win = max(wins.values())
        smith_set = set(c for c in candidates if wins[c] == max_win)
        old_smith_set = set()
        while smith_set.difference(old_smith_set):
            old_smith_set = smith_set.copy()
            for c in old_smith_set:
                for tup,val in margins.items():
                    if tup[1] == c and val >= 0:
                        smith_set.add(tup[0])
        
        part_index = rparts_index = 0
        part = set()
        fail = False
        for c in rp_result:
            if part_index >= len(part):
                part = rparts_result[rparts_index]
                rparts_index += 1
                part_index = 0
            if c not in part:
                # if verbose:
                print(f"{'\033[31m'}Test {i+1} failed: {c} not in {part}{'\033[0m'}")
                print(f"Candidates: {candidates}")
                print(f"Votes:")
                for vote in votes:
                    print(vote)
                print(f"Ranked Pairs Result: {rp_result}")
                print(f"Ranked Partitions Result: {rparts_result}")
                print(f"Smith Set: {smith_set}")
                fail = True
                break
            part_index += 1
        if not fail:
            if verbose:
                print(f"{'\033[32m'}Test {i+1} passed.{'\033[0m'}")
                print(f"Candidates: {candidates}")
                # print(f"Votes:")
                # for vote in votes:
                #     print(vote)
                print(f"Ranked Pairs Result: {rp_result}")
                print(f"Ranked Partitions Result: {rparts_result}")
                print(f"Smith Set: {smith_set}")
            passed += 1
    print(f"{passed}/{NUM_TESTS} tests passed.")

def partition_trials(A=500, V=25, target=[50,10]):
    alternatives = list(range(A))
    # votes = generate_random_partition_votes(alternatives, V, [10/A, 1-10/A-2/A], [0])
    # votes = generate_random_partition_votes(alternatives, V, [0.01,0.02,0.05,0.915], [0])
    # votes = generate_random_partition_votes(alternatives, V, [1/A]*A, [0])
    votes = generate_random_partition_votes(alternatives, V, [20/A], [10/A])
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
    cyclesm = timed_ranked_partitions_with_margins(alternatives, votes)

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
    # trial_strata.to_csv("./data/partitions/weighted_strata.csv", index=False)\

if __name__ == "__main__":
    ranked_pairs_ranked_partitions_equivalence(2,10,20,100)
    
    # ranked_pairs_ranked_partitions_equivalence()
    
    # pairs = pairwise_margins(
    #         ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'], 
    #         [['16', '11', '3', '13', '4', '15', '14', '8', '0', '1', '5', '9', '2', '6', '7', '12', '10'],
    #         ['10', '0', '5', '2', '7', '14', '11', '9', '12', '8', '6', '16', '4', '1', '15', '13', '3'],
    #         ['3', '5', '1', '14', '7', '11', '0', '12', '6', '15', '2', '9', '16', '13', '4', '8', '10'],
    #         ['15', '1', '8', '4', '2', '16', '12', '5', '14', '10', '0', '9', '7', '13', '6', '11', '3'],
    #         ['10', '7', '15', '16', '0', '5', '2', '9', '1', '12', '3', '8', '11', '13', '4', '6', '14'],
    #         ['15', '13', '7', '11', '3', '6', '9', '14', '0', '8', '4', '16', '2', '12', '1', '10', '5'],
    #         ['0', '14', '8', '10', '6', '13', '2', '3', '12', '5', '7', '9', '15', '1', '16', '4', '11'],
    #         ['9', '3', '7', '4', '11', '5', '15', '1', '13', '6', '8', '2', '12', '14', '16', '0', '10'],
    #         ['5', '10', '3', '8', '9', '13', '7', '12', '1', '15', '0', '14', '4', '16', '2', '6', '11'],
    #         ['0', '6', '13', '2', '1', '12', '14', '8', '10', '7', '4', '16', '3', '11', '15', '5', '9'],
    #         ['5', '11', '4', '13', '8', '1', '3', '9', '14', '0', '16', '10', '15', '12', '6', '2', '7'],
    #         ['15', '7', '1', '8', '12', '13', '6', '11', '16', '3', '9', '10', '14', '0', '2', '4', '5'],
    #         ['9', '6', '15', '5', '2', '11', '7', '12', '14', '16', '10', '4', '13', '0', '1', '3', '8'],
    #         ['8', '14', '9', '4', '10', '7', '1', '3', '5', '15', '11', '2', '16', '6', '13', '0', '12']]
    #     )
    # grouped_pairs = {} # strength:[edges]
    # for tup,val in pairs.items():
    #     grouped_pairs.setdefault(val,[]).append(tup)
    # for group in grouped_pairs.keys():
    #     if group < 0:
    #         continue
    #     print(f"{group}: {grouped_pairs[group]}")