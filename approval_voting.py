def approval_voting(candidates, votes):
    pass

def proportional_approval_voting(candidates:list, votes:list[list[set]]):
    pass

def greedy_approval_voting(candidates:list, votes:list[list[set]]):
    pass

def weighted_approval_voting(candidates:list, votes:list, weights=lambda vote: [1-i*1/len(vote) for i in range(len(vote))]):
    pass