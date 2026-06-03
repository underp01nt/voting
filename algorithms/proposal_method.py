import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rankings import generate_random_votes

# candidates: array of strings; list of candidate names
# preference_profiles: array of arrays of strings; list of voters' preferences,
# where each preference is an array listing their desired ranking of candidates.
def honest_election(candidates, preference_profiles):
    ranking = []
    elections = []
    place = 0
    
    while (len(ranking) < len(candidates)):
        round = 0
        place += 1
        
        remaining_candidates = [c for c in candidates if c not in ranking]
        
        # run votes until only one candidates remains
        while (len(remaining_candidates) > 1):
            round += 1
            counts = {c:0 for c in remaining_candidates}
            counts['Place'] = str(place)
            counts['Round'] = str(round)
            for profile in preference_profiles:
                votes = len(remaining_candidates)-1
                i = 0
                while votes > 0:
                    if profile[i] in remaining_candidates:
                        counts[profile[i]] += 1
                        votes -= 1
                    i += 1
            # elections[round] = counts
            elections.append(counts)
            
            # remove candidate with least votes
            minimum_votes = min(counts[c] for c in remaining_candidates)
            for candidate in counts:
                if candidate in remaining_candidates and counts[candidate] == minimum_votes:
                    remaining_candidates.remove(candidate)
                
        if (len(remaining_candidates) == 0):
            print(ranking)
            raise Exception("Tie")
        
        ranking.append(remaining_candidates[0])
        
        # elections[round] = {remaining_candidates[0] : len(preference_profiles)}
        elections.append({remaining_candidates[0] : len(preference_profiles), 'Place': str(place), 'Round': 'W'})
        
    return ranking, pd.DataFrame(elections).set_index(['Place','Round'], drop=True)

def plot_elections(elections: pd.DataFrame, title:str='Votes per Round'):
    plot = elections.plot(kind='bar')
    plt.title(title)
    plt.xlabel('Round')
    plt.ylabel('Votes')
    
    plt.show()
    


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
    
    # rankings = generate_random_votes(15, candidates)
    
    candidates = ['A', 'B', 'C']
    rankings = [['A', 'B','C']] * 24 + [['C', 'A', 'B']] * 14 + [['C', 'B', 'A']] * 12
    
    ranking, elections = honest_election(candidates, rankings)
    
    print(ranking)
    print(elections)
    # pd.DataFrame(rankings).to_csv('./data/rankings.csv', index=False)
    # elections.to_csv('./data/elections.csv')
    
    plot_elections(elections, title='Not Condorcet')