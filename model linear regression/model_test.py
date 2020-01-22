import pickle
import cloud
import hybrid
import numpy as np
import time

def minMaxQos(num_act, actGraph):
    servicesMin = []
    servicesMax = []
    listQos = []
    for i in range(num_act):
        servicesMin.append([cloud.Service(i, 0.1, 0.7, 0.9, 0.1, matching=1)])
        servicesMax.append([cloud.Service(i, 5, 0.95, 0.99, 3, matching=1)])

    cpMin = cloud.CompositionPlan(actGraph, servicesMin)
    cpMax = cloud.CompositionPlan(actGraph, servicesMax)

    k = [cpMin.cpResponseTime(), cpMin.cpPrice(),cpMin.cpAvailability(), cpMin.cpReliability()]
    L = ['responseTime', 'price', 'availability', 'reliability']
    minQos = {i: j for i, j in zip(L, k)}

    k = [cpMax.cpResponseTime(), cpMax.cpPrice(), cpMax.cpAvailability(), cpMax.cpReliability()]
    L = ['responseTime', 'price', 'availability', 'reliability']
    maxQos = {i: j for i, j in zip(L, k)}

    return minQos, maxQos


def generateActGraph(num_act):       # Sequential
    return [[i, i + 1, 0] for i in range(num_act - 1)]


def generateCandidates(num_act, num_candidates):
    candidates = []
    for i in range(num_act):
        s = []
        for j in range(num_candidates):
            responseTime = np.random.uniform(0.1, 5, 1)[0]
            price = np.random.uniform(0.1, 3, 1)[0]
            availability = np.random.uniform(0.9, 0.99, 1)[0]
            reliability = np.random.uniform(0.7, 0.95, 1)[0]
            s.append(cloud.Service(i, responseTime, reliability, availability, price, matching=1))
        candidates.append(s)
    return candidates


def test(num_act, num_candidates,sn,mcn,sq, constraints, weightList):

    x = str((num_act, num_candidates,sn,mcn,sq))
    y = []
    z = []

    actGraph = generateActGraph(num_act)

    print("Generating random candidates for {} ...".format(x))

    candidates = generateCandidates(num_act, num_candidates)

    print("Done !")

    # minQos and maxQos definition

    minQos, maxQos = minMaxQos(num_act, actGraph)


    # optimal fitness
    opt = 2.0


    # Algorithm execution

    print("Executing Algorithm ")
    start_time = time.time()
    _ , fit = hybrid.ABCgenetic(actGraph, candidates, workers=sn//2, onlookers=sn//2, scouts=sn//2, SQ=sq, MCN=mcn, SN=sn, minQos=minQos, maxQos=maxQos, constraints=constraints, weightList=weightList)
    rt = time.time() - start_time


    print("fitness = {}\nScalability = {}".format(fit/opt,rt))


# main

with open("model.pkl", 'rb') as file:
    model = pickle.load(file)

# input
constraints = {'responseTime': 10, 'price': 1000, 'availability': 10, 'reliability': 10}
weightList = [0.25, 0.25, 0.25, 0.25]
x1 = int(input("NUMBER OF ACTIVITIES : "))
x2 = int(input("NUMBER OF CANDIDATE SERVICES : "))
Xnew = np.array([x1,x2,1,0]).reshape(-1,4)

# predict
Ynew = model.predict(Xnew)
print("RECOMMENDED : ")
print("Iterations = {}\nScouts condition = {}\nFood Sources = {}\n".format(int(Ynew[0][0]),int(Ynew[0][1]),int(Ynew[0][2])))
test(x1, x2,int(Ynew[0][2]),int(Ynew[0][0]),int(Ynew[0][1]), constraints, weightList)