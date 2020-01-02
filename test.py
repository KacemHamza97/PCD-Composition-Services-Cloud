import cloud
import hybrid
import numpy as np
import time

def minMaxQos():
    global listQos , minQos , maxQos
    for j in ['responseTime', 'price', 'availability', 'reliability']:
        minQos[j] = min(i[j] for i in listQos)
        maxQos[j] = max(i[j] for i in listQos)


def updateListQos(compositionPlan):
    global listQos , minQos , maxQos
    k = [compositionPlan.evaluateResponseTime(), compositionPlan.evaluatePrice(),
         compositionPlan.evaluateAvailability(), compositionPlan.evaluateReliability()]
    L = ['responseTime', 'price', 'availability', 'reliability']
    d = {i: j for i, j in zip(L, k)}
    listQos.append(d)


actGraph = [[1, 2, 0], [2, 3, 0], [3 ,4 , 0], [4, 5, 0]]

rootAct = 1

candidates = []

minQos = {}

maxQos = {}

for i in range(1,6) :
    s = []
    for j in range(100) :
        price = np.random.uniform(0.2,0.95,1)[0]
        responseTime = np.random.normal(0.5, 0.4 ,1)[0]
        availability = np.random.uniform(0.9,0.99,1)[0]
        reliability = np.random.uniform(0.7,0.95,1)[0]
        s.append(cloud.Service(i, responseTime, reliability, availability, price, matching=1))
    candidates.append(s)

# minQos and maxQos definition

listQos = []
for i in range(10) :
    x = cloud.randomCompositionPlan(rootAct, actGraph, candidates)
    updateListQos(x)
minMaxQos()

# optimal fitness
l = []
print("Finding Optimal solution takes a few minutes ...")
for i in range(100) :
    x = hybrid.ABCgenetic(rootAct, actGraph, candidates, SQ = 3, MCN = 100, SN = 100, p = 0.5 , minQos = minQos , maxQos = maxQos )
    l.append(x)

opt = max(l)

# algorithm efficiency
print("          Execution          |           Fitness           |        ExecutionTime        |           Optimal           |        Deviation        ")
for i in range(10) :
    start_time = time.time()
    X = hybrid.ABCgenetic(rootAct, actGraph, candidates, SQ = 3, MCN = 100, SN = 50, p = 0.5 , minQos = minQos , maxQos = maxQos )
    print("             ",i,"             |      %.16f     |    %.17f      |    %.16f       |  %.16f  " % (X / opt ,time.time() - start_time ,opt,opt-X))
