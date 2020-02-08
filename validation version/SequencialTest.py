import cloud
import hybrid
import numpy as np
import time
import csv

def minMaxOpt(actNum, actGraph):
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


def generateActGraph(actNum):       # Sequential
    return [[i, i + 1, 0] for i in range(actNum - 1)]


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
actNum = int(input("NUMBER OF ACTIVITIES : "))
num_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': actNum * 0.3, 'price': actNum * 1.55, 'availability': 0.945 ** actNum, 'reliability': 0.825 ** actNum}
weightList = [0.25, 0.25, 0.25, 0.25]
actGraph = generateActGraph(actNum)
servicesOpt , minQos, maxQos = minMaxOpt(actNum, actGraph)
candidates = generateCandidates(actNum, num_candidates,servicesOpt)

# optimal fitness
opt = 2.0

while True :

    mcn = int(input("ITERATION NUMBER : "))
    sq = int(input("SCOUT CONDITION : "))

    print("Executing Algorithm ")
    start_time = time.time()
    _ , fit = hybrid.ABCgenetic(actGraph, candidates,SQ=sq, MCN=mcn,minQos=minQos, maxQos=maxQos, constraints=constraints, weightList=weightList)
    rt = time.time() - start_time

    with open('Sequencialdataset.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([actNum,num_candidates,sq, mcn,fit / opt ,rt])

    print("fitness = {}\nScalability = {}\nDone !".format(fit / opt,rt))
