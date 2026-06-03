import numpy as np
import pandas as pd

# candidates: array of candidate names, 
# votes: array of rankings (arrays of candidate names in order of preference)
# returns a dict of *all* pairwise (order dependent) vote totals
def pairwise_comparison(candidates:list, votes:list[list]):
    pairs = {
        (a, b) : 0 for a in candidates for b in candidates if a != b
        }
    
    for vote in votes:
        for i in range(len(vote)-1):
            for j in range(i+1, len(vote)):
                if type(vote[i]) == set:
                    for c1 in vote[i]:
                        if type(vote[j]) == set:
                            for c2 in vote[j]:
                                pairs[(c1, c2)] += 1
                        else:
                            pairs[c1, vote[j]] += 1
                else:
                    if type(vote[j]) == set:
                            for c2 in vote[j]:
                                pairs[(vote[i], c2)] += 1
                    else:
                        pairs[(vote[i], vote[j])] += 1
                
    return pairs

def pairwise_wins(candidates:list, votes:list[list]):
    pairs = pairwise_comparison(candidates, votes)
    return {(a,b): pairs[(a,b)] for a,b in pairs.keys() if pairs[(a,b)] >= pairs[(b,a)]}  

def pairwise_margins(candidates:list, votes:list[list]):
    pairs = pairwise_comparison(candidates,votes)
    return {(a,b) : (pairs[(a,b)]-pairs[(b,a)]) for a,b in pairs.keys()}

def weighted_pairwise_comparison(candidates:list, votes:list[list], pos_weights, neg_weights=lambda vote: [0]*len(vote)):
    pairs = {
        (a, b) : 0 for a in candidates for b in candidates if a != b
        }
    
    for vote in votes:
        pw = pos_weights(vote)
        nw = neg_weights(vote)
        for i in range(len(vote)-1):
            for j in range(i+1, len(vote)):
                if type(vote[i]) == set:
                    for c1 in vote[i]:
                        if type(vote[j]) == set:
                            for c2 in vote[j]:
                                pairs[(c1, c2)] += pw[i] - nw[j]
                        else:
                            pairs[c1, vote[j]] += pw[i] - nw[j]
                else:
                    if type(vote[j]) == set:
                            for c2 in vote[j]:
                                pairs[(vote[i], c2)] += pw[i] - nw[j]
                    else:
                        pairs[(vote[i], vote[j])] += pw[i] - nw[j]
                
    return pairs

def matrix_of_majorities(candidates:list, votes:list[list]):
    matrix = np.zeros((len(candidates), len(candidates)), dtype=int)
    for vote in votes:
        for i in range(len(vote)-1):
            for j in range(i+1, len(vote)):
                matrix[candidates.index(vote[i])][candidates.index(vote[j])] += 1
    return matrix, candidates # basis

def generate_random_votes(candidates, n):
    from random import choice
    preferences = []
    for _ in range(n):
        remaining_candidates = [c for c in candidates]
        vote = []
        
        while (remaining_candidates):
            candidate = choice(remaining_candidates)
            vote.append(candidate)
            remaining_candidates.remove(candidate)
        preferences.append(vote)

    return preferences

def generate_random_approval_votes(alternatives, n, approval_prob=0.1):
    votes = []
    for _ in range(n):
        vote = [set(), set()]
        for alt in alternatives:
            if np.random.rand() < approval_prob: # chance to approve each alternative
                vote[0].add(alt)
            else:
                vote[1].add(alt)
        votes.append(vote)
    return votes

def generate_random_approval_disapproval_votes(alternatives, n, approval_prob=0.1, disapproval_prob=0.1):
    votes = []
    for _ in range(n):
        vote = [set(), set(), set()]
        for alt in alternatives:
            rand_val = np.random.rand()
            if rand_val < approval_prob: # chance to approve each alternative
                vote[0].add(alt)
            elif rand_val < approval_prob + disapproval_prob: # chance to disapprove each alternative
                vote[2].add(alt)
            else:
                vote[1].add(alt)
        votes.append(vote)
    return votes

def generate_random_partition_votes(alternatives, n, part_prob=[0.1,0.2], part_var=[0.05,0.1]):
    votes = []
    if sum(part_prob) < 1:
        part_prob.append(1-sum(part_prob))
    for _ in range(n):
        if len(part_var) <= len(part_prob):
            vote_prob = part_prob[:]
            for i in range(len(part_var)):
                new_val = vote_prob[i]+(2*np.random.rand()-1)*part_var[i]
                vote_prob[i] = new_val if new_val >= 0 else 0
            if sum(vote_prob) < 1:
                vote_prob[-1] += 1-sum(vote_prob)
        else:
            vote_prob = part_prob
        vote = [set() for _ in range(len(vote_prob))]
        for alt in alternatives:
            rand_val = np.random.rand()
            prob_sum = 0
            for i, prob in enumerate(vote_prob):
                prob_sum += prob
                if rand_val < prob_sum:
                    # print(f"{rand_val}, {prob_sum}, {i}, {alt}")
                    vote[i].add(alt)
                    # print(vote[i])
                    break
        votes.append([v for v in vote if len(v) != 0])
    return votes

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