import cloud
import hybrid
import numpy as np
import time

actGraph = [[1, 2, 0], [2, 3, 1], [2, 4, 1], [4, 5, -1], [4, 6, -1]]

rootAct = 1

candidates = []

for i in range(1,7) :
    s = []
    for j in range(10) :
        price = np.random.uniform(0.2,0.95,1)[0]
        responseTime = np.random.normal(0.5, 0.4 ,1)[0]
        availability = np.random.uniform(0.9,0.99,1)[0]
        reliability = np.random.uniform(0.7,0.95,1)[0]
        s.append(cloud.Service(i, responseTime, reliability, availability, price, matching=1))
    candidates.append(s)

# optimal fitness
l = []
print("Finding Optimal solution takes a few minutes ...")
for i in range(1000) :
    l.append(hybrid.ABCgenetic(rootAct, actGraph, candidates, 3, 50, 50, 0.3))

opt = max(l)

# algorithm efficiency
print("          Execution          |           Fitness           |        ExecutionTime        |           Optimal           |        Deviation        ")
for i in range(10) :
    start_time = time.time()
    X = hybrid.ABCgenetic(rootAct, actGraph, candidates, 3, 50, 50, 0.3)
    print("             ",i,"             |      %.16f     |    %.17f      |    %.16f       |  %.16f  " % (X ,time.time() - start_time ,opt,opt-X))
