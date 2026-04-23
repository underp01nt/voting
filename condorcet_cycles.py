# import sys
import numpy as np
from itertools import permutations

# sys.setrecursionlimit(10000)

candidates = ('A','B','C','D')

strengths = [1,2,3,4,5,6]

print(len(list(permutations(strengths))))