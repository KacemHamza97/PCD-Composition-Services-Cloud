import networkx
import matplotlib.pyplot as plt
from numpy.random import uniform, choice

from data_structure.Service import Service
from mono_objective_algorithms.experimentation.validation_test.hybrid import ABCgenetic

state = ["over", "precise"]


def generateCandidates(actNum, num_candidates):
    candidates = list()
    for i in range(actNum):
        candidates.append([])
        for j in range(num_candidates):
            responseTime = uniform(0.1, 5, 1)[0]
            price = uniform(0.1, 3, 1)[0]
            availability = uniform(0.9, 0.99, 1)[0]
            reliability = uniform(0.7, 0.95, 1)[0]
            matchingState = choice(state)
            if matchingState == "precise":
                candidates[i].append(Service(i, responseTime, reliability, availability, price, matchingState))
            candidates[i].append(Service(i, responseTime, reliability, availability, price, matchingState))
    return candidates


# main

# input
actNum = 3
actGraph = [[0, 1, 0], [1, 2, 0]]
num_candidates = 5
positions = {0: [0, 0], 1: [1, 0], 2: [2, 0]}
G = networkx.DiGraph()
G.add_weighted_edges_from(actGraph)
networkx.drawing.nx_pylab.draw_networkx(G, pos=positions)
plt.show()
constraints = {'responseTime': actNum * 0.3, 'price': actNum * 1.55, 'availability': 0.945 ** actNum,
               'reliability': 0.825 ** actNum}
weights = [0.25, 0.25, 0.25, 0.25]
candidates = generateCandidates(actNum, num_candidates)
mcn = 10
sq = 2
sn = 10
result = ABCgenetic(actGraph, candidates, SN=sn, SQ=sq, MCN=mcn, SCP=9 * mcn // 10, N=sn // 2,CP=0.2, constraints=constraints, weights=weights)
