import cloud
import hybrid
import numpy as np
import time
import csv
from math import inf
from pymoo.factory import get_performance_indicator

def generateActGraph(actNum):       # Sequential
    return [[i, i + 1, 0] for i in range(actNum - 1)]


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
actNum = int(input("NUMBER OF ACTIVITIES : "))
num_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': actNum * 0.3, 'price': actNum * 1.55, 'availability': 0.945 ** actNum, 'reliability': 0.825 ** actNum}
actGraph = generateActGraph(actNum)
candidates = generateCandidates(actNum, num_candidates)


while True :

    mcn = int(input("ITERATION NUMBER : "))
    sq = int(input("SCOUT CONDITION : "))


    # true pareto
    print("Finding true pareto ...")
    _ , true_pareto =  hybrid.ABCgenetic(actGraph, candidates,SQ=50, MCN=mcn * 10,constraints=constraints)

    print("Executing Algorithm ")
    start_time = time.time()
    solutions , _ = hybrid.ABCgenetic(actGraph, candidates,SQ=sq, MCN=mcn,constraints=constraints)
    rt = time.time() - start_time

    # max objectives in true_pareto
    max = [- inf,- inf,- inf]
    for i in range(3) :
        for x in true_pareto :
            if max[i] < x[i] :
                max[i] = x[i]

    r = np.array([max[0] * 0.9 , max[1] * 0.9 , max[2] * 1.1])

    # evaluating performance
    gd = get_performance_indicator("gd", true_pareto)
    GD = gd.calc(solutions)

    igd = get_performance_indicator("igd", true_pareto)
    IGD = igd.calc(solutions)

    hv = get_performance_indicator("hv", ref_point = r)
    HV = hv.calc(solutions)

    with open('Sequencialdataset.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([actNum,num_candidates,sq, mcn,rt,GD,IGD,HV])
