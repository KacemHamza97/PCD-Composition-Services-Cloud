import cloud
import hybrid
import numpy as np
import time
import csv

def minMaxOpt(num_act,actGraph):
    servicesMin = []
    servicesMax = []
    servicesOpt = []
    listQos = []
    for i in range(num_act):
        servicesMin.append([cloud.Service(i, 0.1, 0.7, 0.9, 0.1, matching=1)])
        servicesMax.append([cloud.Service(i, 5, 0.95, 0.99, 3, matching=1)])
        servicesOpt.append([cloud.Service(i, 0.1, 0.95, 0.99, 0.1, matching=1)])

    cpMin = cloud.CompositionPlan(actGraph, servicesMin)
    cpMax = cloud.CompositionPlan(actGraph, servicesMax)

    k = [cpMin.cpResponseTime(), cpMin.cpPrice(),cpMin.cpAvailability(), cpMin.cpReliability()]
    L = ['responseTime', 'price', 'availability', 'reliability']
    minQos = {i: j for i, j in zip(L, k)}

    k = [cpMax.cpResponseTime(), cpMax.cpPrice(), cpMax.cpAvailability(), cpMax.cpReliability()]
    L = ['responseTime', 'price', 'availability', 'reliability']
    maxQos = {i: j for i, j in zip(L, k)}

    return servicesOpt,minQos, maxQos


def generateActGraph(num_act):   # actGraph entry
    actGraph = []
    print("BUILDING ACTGRAPH")
    while True :
        ans = input("Enter a new branch ? (y/n)")
        if ans not in {'y','n'} :
            continue
        elif ans == "y" :
            while True :
                try :
                    source = int(input("Source :"))
                    if source not in range(num_act) :
                        print("Check input (source not existing)!")
                        break
                    destination = int(input("Destination :"))
                    if destination not in range(num_act) :
                        print("Check input (destination not existing)!")
                        break
                    type = int(input("Type : "))
                    if type not in {0,-1,1} :
                        print("Check input !")
                        break
                    actGraph.append([source,destination,type])
                    break
                except :
                    print("Check input (must be int)!")
                    break
        else :
            print("Done !")
            break
    return(actGraph)




def generateCandidates(num_act, num_candidates,servicesOpt):
    candidates = servicesOpt
    for i in range(num_act):
        for j in range(num_candidates - 1):
            responseTime = np.random.uniform(0.1, 5, 1)[0]
            price = np.random.uniform(0.1, 3, 1)[0]
            availability = np.random.uniform(0.9, 0.99, 1)[0]
            reliability = np.random.uniform(0.7, 0.95, 1)[0]
            candidates[i].append(cloud.Service(i, responseTime, reliability, availability, price, matching=1))
    return candidates


def test(actGraph,candidates,sn,mcn,sq, constraints, weightList):

    # Algorithm execution

    print("Executing Algorithm ")
    start_time = time.time()
    _ , fit = hybrid.ABCgenetic(actGraph, candidates,SQ=sq, MCN=mcn, SN=sn, minQos=minQos, maxQos=maxQos, constraints=constraints, weightList=weightList)
    rt = time.time() - start_time
    print("fitness = {}\nScalability = {}\nDone !".format(fit / opt,rt))


# main

# input
constraints = {'responseTime': 10, 'price': 10, 'availability': 0.95, 'reliability': 0.8}
weightList = [0.25, 0.25, 0.25, 0.25]
num_act = int(input("NUMBER OF ACTIVITIES : "))
num_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
actGraph = generateActGraph(num_act)
servicesOpt , minQos, maxQos = minMaxOpt(num_act, actGraph)
candidates = generateCandidates(num_act, num_candidates,servicesOpt)

# optimal fitness
opt = 2.0

while True :
    x3 = int(input("SCOUT CONDITION : "))
    x4 = int(input("ITERATION NUMBER : "))
    x5 = int(input("RESSOURCES NUMBER : "))

    test(actGraph,candidates,x5,x4,x3, constraints, weightList)
