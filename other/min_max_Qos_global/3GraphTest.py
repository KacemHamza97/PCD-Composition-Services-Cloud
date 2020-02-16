import cloud
import hybrid
import numpy as np
import time
import csv

def minMaxOpt(actNum,actGraph):
    servicesMin = []
    servicesMax = []
    servicesOpt = []
    for i in range(actNum):
        servicesMin.append([cloud.Service(i, 0.1, 0.7, 0.9, 0.1, matching=1)])
        servicesMax.append([cloud.Service(i, 5, 0.95, 0.99, 3, matching=1)])
        servicesOpt.append([cloud.Service(i, 0.1, 0.95, 0.99, 0.1, matching=1)])

    cpMin = cloud.CompositionPlan(actGraph, servicesMin)
    cpMax = cloud.CompositionPlan(actGraph, servicesMax)

    minQos = cpMin.cpQos()

    maxQos = cpMax.cpQos()

    return servicesOpt,minQos, maxQos

def generateCandidates(actNum, num_candidates,servicesOpt):
    candidates = list()
    for i in range(actNum) :
        candidates.append([servicesOpt[i][0]])
        for j in range(num_candidates - 1):
            responseTime = np.random.uniform(0.1, 5, 1)[0]
            price = np.random.uniform(0.1, 3, 1)[0]
            availability = np.random.uniform(0.9, 0.99, 1)[0]
            reliability = np.random.uniform(0.7, 0.95, 1)[0]
            candidates[i].append(cloud.Service(i, responseTime, reliability, availability, price, matching=1))
    return candidates


# main

# input
weightList = [0.25, 0.25, 0.25, 0.25]
actGraphA = [[0,1,1],[0,2,1],[0,3,1],[1,4,0],[2,5,0],[3,6,0],[4,7,0],[5,7,0],[5,8,0],[6,8,0],[7,9,0],[8,9,0]]
actGraphB = [[0,1,1],[0,2,1],[0,3,1],[0,4,1],[1,5,0],[4,7,0],[2,6,0],[3,6,0],[5,9,0],[6,8,0],[7,8,0],[8,9,0],[9,10,0],[10,11,0],[11,12,1],[11,13,1],[12,14,0],[14,16,0],[13,15,0],[15,17,0],[16,18,0],[17,18,0],[18,19,0]]
actGraphC = [[0,1,1],[0,2,1],[0,3,1],[0,4,1],[1,5,0],[4,7,0],[2,6,0],[3,6,0],[6,9,0],[7,9,0],[5,8,0],[6,8,0],[8,10,0],[9,10,0],[10,11,0],[11,12,0],[12,13,1],[12,14,1],[12,15,1],[12,16,1],[12,17,1],[13,18,0],[18,23,0],[14,19,0],[19,24,0],[15,20,0],[20,25,0],[16,21,0],[21,26,0],[17,22,0],[22,27,0],[23,28,0],[24,28,0],[25,28,0],[26,28,0],[27,28,0],[28,29,0]]

# optimal fitness
opt = 2.0

while True :
    while True :
        t = input("Graph Selected ? (a/b/c)")
        if t in {'a','b','c'} :
            break

    mcn = int(input("ITERATION NUMBER : "))
    sq = int(input("SCOUT CONDITION : "))

    if t == 'a' :
        actGraph = actGraphA
        actNum = 10
        constraints = {'responseTime': 5 * 0.3, 'price': 10 * 1.55, 'availability': 0.945 ** 10 , 'reliability': 0.825 ** 10}
    elif t == 'b' :
        actGraph = actGraphB
        actNum = 20
        constraints = {'responseTime': 12 * 0.3, 'price': 20 * 1.55, 'availability': 0.945 ** 20, 'reliability': 0.825 ** 20}
    else :
        actGraph = actGraphC
        actNum = 30
        constraints = {'responseTime': 12 * 0.3 , 'price': 30 * 1.55, 'availability': 0.945 ** 30, 'reliability': 0.825 ** 30}


    num_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))

    servicesOpt , minQos, maxQos = minMaxOpt(actNum, actGraph)
    candidates = generateCandidates(actNum, num_candidates,servicesOpt)

    print("Executing Algorithm ")
    start_time = time.time()
    _ , fit = hybrid.ABCgenetic(actGraph, candidates,MCN=mcn,SQ=sq,minQos=minQos, maxQos=maxQos, constraints=constraints, weightList=weightList)
    rt = time.time() - start_time

    with open('3GraphTestdataset.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([t,num_candidates,sq, mcn, fit / opt ,rt])

    print("fitness = {}\nScalability = {}\nDone !".format(fit / opt,rt))
