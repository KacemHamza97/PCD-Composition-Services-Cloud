import cloud
import hybrid
import numpy as np
import time
import csv
import networkx
import matplotlib.pyplot as plt


state = ["over" , "precise"]

def generateCandidates(actNum, num_candidates):
    candidates = list()
    for i in range(actNum) :
        candidates.append([])
        for j in range(num_candidates):
            responseTime = np.random.uniform(0.1, 5, 1)[0]
            price = np.random.uniform(0.1, 3, 1)[0]
            availability = np.random.uniform(0.9, 0.99, 1)[0]
            reliability = np.random.uniform(0.7, 0.95, 1)[0]
            matchingState = np.random.choice(state)
            if matchingState == "precise" :
                candidates[i].append(cloud.Service(i, responseTime, reliability, availability, price, matchingState))
            candidates[i].append(cloud.Service(i, responseTime, reliability, availability, price, matchingState))
    return candidates

# main

# input
actNum = 3
actGraph = [[0,1,0],[1,2,0]]
num_candidates = 5
positions = {0:[0,0],1:[1,0],2:[2,0]}
G = networkx.DiGraph()
G.add_weighted_edges_from(actGraph)
networkx.drawing.nx_pylab.draw_networkx(G,pos = positions)
plt.show()
constraints = {'responseTime': actNum * 0.3, 'price': actNum * 1.55, 'availability': 0.945 ** actNum, 'reliability': 0.825 ** actNum}
weights = [0.25, 0.25, 0.25, 0.25]
candidates = generateCandidates(actNum, num_candidates)
mcn = 10
sq = 2
sn = 10
result = hybrid.ABCgenetic(actGraph, candidates,SN = sn ,SQ=sq ,MCN=mcn,constraints=constraints, weights=weights)
