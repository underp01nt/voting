import pandas as pd
import numpy as np

# candidates: array of strings; list of candidate names
# preference_profiles: array of arrays of strings; list of voters' preferences,
# where each preference is an array listing their desired ranking of candidates.
def honest_election(candidates, preference_profiles):
    ranking = []
    elections = []
    
    while (len(ranking) < len(candidates)):
        remaining_candidates = [c for c in candidates if c not in ranking]
        
        # run votes until only one candidates remains
        while (len(remaining_candidates) > 1):
            counts = {c:0 for c in candidates}
            for profile in preference_profiles:
                votes = len(remaining_candidates)-1
                i = 0
                while votes > 0:
                    if profile[i] in remaining_candidates:
                        counts[profile[i]] += 1
                        votes -= 1
                    i += 1
            elections.append(counts)
            
            # remove candidate with least votes
            minimum_votes = min(counts[c] for c in remaining_candidates)
            to_be_removed = []
            for candidate in counts:
                if candidate in remaining_candidates and counts[candidate] == minimum_votes:
                    remaining_candidates.remove(candidate)
                
            
        ranking.append(remaining_candidates[0])
    
    return ranking, pd.DataFrame(elections)

def plot_elections(elections):
    import matplotlib.pyplot as plt
    for c in elections.rows:
        plt.plot(elections[c], label=c)
    plt.legend()
    plt.xlabel('Round')
    plt.ylabel('Votes')
    plt.title('Votes per Round')
    plt.show()
    
def generate_random_votes(n, candidates):
    preferences = []
    for _ in range(n):
        remaining_candidates = [c for c in candidates]
        vote = []
        
        while (remaining_candidates):
            candidate = np.random.choice(remaining_candidates)
            vote.append(candidate)
            remaining_candidates.remove(candidate)
        preferences.append(vote)

    return preferences

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
    
    ranking, elections = honest_election(candidates, rankings)
    
    print(ranking)
    elections.to_csv('./elections.csv', index=False)