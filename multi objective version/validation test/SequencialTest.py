import cloud
import hybrid
import numpy as np
import time
import csv
import networkx
import matplotlib.pyplot as plt


def generateCandidates(actNum, num_candidates):
    candidates = list()
    for i in range(actNum) :
        candidates.append([])
        for j in range(num_candidates):
            responseTime = np.random.uniform(0.1, 5, 1)[0]
            price = np.random.uniform(0.1, 3, 1)[0]
            availability = np.random.uniform(0.9, 0.99, 1)[0]
            reliability = np.random.uniform(0.7, 0.95, 1)[0]
            candidates[i].append(cloud.Service(i, responseTime, reliability, availability, price, matching=1))
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
candidates = generateCandidates(actNum, num_candidates)
mcn = 10
sq = 2
result = hybrid.ABCgenetic(actGraph, candidates,SQ=sq ,MCN=mcn,constraints=constraints)
for cp in result :
    print(f"possible solution :\n{cp.cpQos()}\n")
