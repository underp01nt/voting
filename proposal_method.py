import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from votingutils import generate_random_votes

# candidates: array of strings; list of candidate names
# preference_profiles: array of arrays of strings; list of voters' preferences,
# where each preference is an array listing their desired ranking of candidates.
def honest_election(candidates, preference_profiles):
    ranking = []
    elections = []
    place = 0
    removed = []
    
    while (len(removed) < len(candidates)):
        round = 0
        place += 1
        
        remaining_candidates = [c for c in candidates if c not in removed]
        
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
            
            # if all candidates have least votes, result is a tie
            if list(counts.values()).count(minimum_votes) == len(remaining_candidates):
                ranking.append(set(remaining_candidates))
                for c in remaining_candidates:
                    removed.append(c)
                elections.append(
                    {c : len(preference_profiles) for c in remaining_candidates} | {
                    'Place': str(place), 
                    'Round': 'T'
                    })
            
            for candidate in counts:
                if candidate in remaining_candidates and counts[candidate] == minimum_votes:
                    remaining_candidates.remove(candidate)
                
        if (len(remaining_candidates) > 0):
            ranking.append(remaining_candidates[0])
            removed.append(remaining_candidates[0])
            elections.append({
                remaining_candidates[0] : len(preference_profiles), 
                'Place': str(place), 
                'Round': 'W'
                })
        
    return ranking, pd.DataFrame(elections).set_index(['Place','Round'], drop=True)

def plot_elections(elections: pd.DataFrame, title:str='Votes per Round', block=False):
    plot = elections.plot(kind='bar',)
    plt.title(title)
    plt.xlabel('Round')
    plt.ylabel('Votes')
    plt.legend(loc='upper right')
    plt.show(block=block)


if __name__ == "__main__":
    # candidates = ['A', 'B', 'C', 'D']
    # rankings = [
    #     ['A', 'B', 'C', 'D'],
    #     ['A', 'B', 'C', 'D'],
    #     ['A', 'B', 'D', 'C'],
    #     ['B', 'A', 'C', 'D'],
    #     ['C', 'D', 'A', 'B'],
    #     ['C', 'D', 'A', 'B'],
    #     ['C', 'D', 'A', 'B'],
    #     ['C', 'D', 'B', 'A'],
    #     ['D', 'C', 'B', 'A'],
    #     ['D', 'C', 'B', 'A'],
    # ]
    
    # rankings = generate_random_votes(candidates, 15)
    
    candidates1 = ['A', 'B', 'C']
    rankings1 = [['A', 'C','B']] * 40 + [['B', 'C', 'A']] * 30 + [['B', 'A', 'C']] * 30
    
    ranking1, elections1 = honest_election(candidates1, rankings1)
    
    print(ranking1)
    print(elections1)
    
    candidates2 = ['A', 'B']
    rankings2 = [['A', 'B']] * 40 + [['B', 'A']] * 30 + [['B', 'A']] * 30
    
    ranking2, elections2 = honest_election(candidates2, rankings2)
    
    print(ranking2)
    print(elections2)
    
    plot_elections(elections1, title='With Losing Candidate C')
    plot_elections(elections2, title='Without Losing Candidate C')
    
    
    # candidates_1 = ['A', 'B', 'C']
    # rankings_1 = [['A', 'B','C']] * 52 + [['C', 'B', 'A']] * 48
    
    # candidates_2 = ['A', 'B', 'C', 'b']
    # rankings_2 = [['A', 'B', 'b', 'C']] * 26 + [['A', 'b', 'B', 'C']] * 26 + [['C', 'B', 'b', 'A']] * 24 + [['C', 'b', 'B', 'A']] * 24

    # ranking_1, elections_1 = honest_election(candidates_1, rankings_1)
    # ranking_2, elections_2 = honest_election(candidates_2, rankings_2)

    # print(ranking_1)
    # print(elections_1)
    # print(ranking_2)
    # print(elections_2)
    
    # plot_elections(elections_1, title='Normal Election')
    # plot_elections(elections_2, title='Attack of the Clones')
    plt.show()