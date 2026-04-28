import numpy as np

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