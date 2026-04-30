import numpy as np
import pandas as pd

# candidates: array of candidate names, 
# votes: array of rankings (arrays of candidate names in order of preference)
# returns a dict of *all* pairwise (order dependent) vote totals
def pairwise_comparison(candidates:list, votes:list):
    pairs = {
        (a, b) : 0 for a in candidates for b in candidates if a != b
        }
    
    for vote in votes:
        for i in range(len(vote)-1):
            for j in range(i+1, len(vote)):
                pairs[(vote[i], vote[j])] += 1
                
    return pairs

def generate_random_votes(candidates, n):
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

def ranking_to_string(ranking):
    string = ""
    for candidate in ranking:
        if type(candidate) == set:
            for c in candidate:
                string += c + " = "
            string = string[:-3] + " > "
        else:
            string += candidate + " > "
    return string[:-3]

def ranking_to_df(ranking):
    place_list = []
    place = 1
    for candidate in ranking:
        if type(candidate) == set:
            for c in candidate:
                place_list.append({'Place': place, 'Candidate': c})
        else:
            place_list.append({'Place': place, 'Candidate': candidate})
        place += 1
    return pd.DataFrame(place_list, columns=['Place', 'Candidate'])