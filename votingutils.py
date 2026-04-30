import numpy as np
import pandas as pd

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