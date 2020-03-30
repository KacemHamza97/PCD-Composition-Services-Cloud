import numpy as np
import time
import csv

from data_structure.Service import Service
from mono_objective_algorithms.algorithms.main.hybrid import ABCgenetic
from mono_objective_algorithms.algorithms.main.ABC import ABC
from mono_objective_algorithms.algorithms.main.genetic import genetic
from mono_objective_algorithms.algorithms.objective_function.fitness import fit

state = ["over", "precise"]


def generateActGraph(actNum):  # Sequential
    return [[i, i + 1, 0] for i in range(actNum - 1)]


def generateCandidates(actNum, num_candidates):
    candidates = list()
    for i in range(actNum):
        candidates.append([])
        for j in range(num_candidates):
            responseTime = np.random.uniform(0.1, 5, 1)[0]
            price = np.random.uniform(0.1, 3, 1)[0]
            availability = np.random.uniform(0.9, 0.99, 1)[0]
            reliability = np.random.uniform(0.7, 0.95, 1)[0]
            matchingState = np.random.choice(state)
            if matchingState == "precise":
                candidates[i].append(Service(i, responseTime, reliability, availability, price, matchingState))
            candidates[i].append(Service(i, responseTime, reliability, availability, price, matchingState))
    return candidates


# main

# input
actNum = int(input("NUMBER OF ACTIVITIES : "))
num_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': actNum * 0.3, 'price': actNum * 1.55, 'availability': 0.945 ** actNum,
               'reliability': 0.825 ** actNum}
weights = [0.25, 0.25, 0.25, 0.25]
actGraph = generateActGraph(actNum)
candidates = generateCandidates(actNum, num_candidates)

mcn = int(input("ITERATION NUMBER : "))
sn = int(input("RESSOURCES NUMBER : "))
sq = int(input("SCOUTS CONDITION : "))

# optimal fitness
print("optimal fitness search !")
opt, _, _ = ABCgenetic(actGraph, candidates, SN=sn, SQ=100, MCN=mcn * 10,SCP=9 * mcn // 10, N=sn // 2,CP=0.2, constraints=constraints, weights=weights)
print("\nDone !")

rt = 0
fit_prev = 0
div = 0
conv = []
normalized_fitness = 0
for itera in range(30) : 
    print(f"Executing Algorithm : hybrid {itera+1}/30")
    start_time = time.time()
    result, minQos, maxQos = ABCgenetic(actGraph, candidates, SN=sn, SQ=sq, MCN=mcn ,SCP=9 * mcn // 10, N=sn // 2,CP=0.2, constraints=constraints, weights=weights)
    rt += (time.time() - start_time) / 30
    normalized_fitness += (fit(result, minQos, maxQos, weights) / fit(opt, minQos, maxQos, weights)) / 30
    div += abs(fit(result, minQos, maxQos, weights)-fit_prev) / 30
    res_prev = fit(result, minQos, maxQos, weights)
    if fit(result, minQos, maxQos, weights)-fit(res_prev, minQos, maxQos, weights) :
        conv.append(itera)

conv = min(conv) 

with open('test_results.csv', mode='a') as file:
    file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    file_writer.writerow(["hybrid",actNum, num_candidates, sn, sq, mcn, normalized_fitness, rt,div,conv])


rt = 0
fit_prev = 0
div = 0
conv = []
normalized_fitness = 0
for itera in range(30) : 
    print(f"Executing Algorithm : abc {itera+1}/30")
    start_time = time.time()
    result, minQos, maxQos = ABC(actGraph, candidates, SN=sn,SQ=sq, MCN=mcn, N=sn // 2, constraints=constraints, weights=weights)
    rt += (time.time() - start_time) / 30
    normalized_fitness += (fit(result, minQos, maxQos, weights) / fit(opt, minQos, maxQos, weights)) / 30
    div += abs(fit(result, minQos, maxQos, weights)-fit(res_prev, minQos, maxQos, weights)) / 30
    fit_prev = fit(result, minQos, maxQos, weights)
    if fit(result, minQos, maxQos, weights)-fit(res_prev, minQos, maxQos, weights) :
        conv.append(itera)

conv = min(conv) 

with open('test_results.csv', mode='a') as file:
    file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    file_writer.writerow(["ABC",actNum, num_candidates, sn, sq, mcn, normalized_fitness, rt,div,conv])


rt = 0
fit_prev = 0
div = 0
conv = []
normalized_fitness = 0
for itera in range(30) : 
    print(f"Executing Algorithm : genetic {itera+1}/30")
    start_time = time.time()
    result, minQos, maxQos = genetic(actGraph, candidates, SN=sn,CP=0.7, constraints=constraints, weights=weights)
    rt += (time.time() - start_time) / 30
    normalized_fitness += (fit(result, minQos, maxQos, weights) / fit(opt, minQos, maxQos, weights)) / 30
    div += abs(fit(result, minQos, maxQos, weights)-fit(res_prev, minQos, maxQos, weights)) / 30
    fit_prev = fit(result, minQos, maxQos, weights)
    if fit(result, minQos, maxQos, weights)-fit(res_prev, minQos, maxQos, weights) :
        conv.append(itera)

conv = min(conv) 

with open('test_results.csv', mode='a') as file:
    file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    file_writer.writerow(["genetic",actNum, num_candidates, sn, sq, mcn, normalized_fitness, rt,div,conv])