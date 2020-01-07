import cloud
import hybrid
import numpy as np
import time
import matplotlib.pyplot as plt
import csv


def minMaxQos(rootAct, num_act, actGraph):
    servicesMin = []
    servicesMax = []
    listQos = []
    for i in range(1, num_act + 1):
        servicesMin.append([cloud.Service(i, 1.4, 0.7, 0.9, 0.95, matching=1)])
        servicesMax.append([cloud.Service(i, 0.01, 0.95, 0.99, 0.2, matching=1)])

    cpMin = cloud.randomCompositionPlan(rootAct, actGraph, servicesMin)
    cpMax = cloud.randomCompositionPlan(rootAct, actGraph, servicesMax)

    k = [cpMin.evaluateResponseTime(), cpMin.evaluatePrice(),
         cpMin.evaluateAvailability(), cpMin.evaluateReliability()]
    L = ['responseTime', 'price', 'availability', 'reliability']
    minQos = {i: j for i, j in zip(L, k)}

    k = [cpMax.evaluateResponseTime(), cpMax.evaluatePrice(),
         cpMax.evaluateAvailability(), cpMax.evaluateReliability()]
    L = ['responseTime', 'price', 'availability', 'reliability']
    maxQos = {i: j for i, j in zip(L, k)}

    return minQos, maxQos


def generateActGraph(num_act):
    return [[i, i + 1, 0] for i in range(1, num_act)]


def generateCandidates(num_act, num_candidates):
    candidates = []
    for i in range(1, num_act + 1):
        s = []
        for j in range(num_candidates):
            price = np.random.uniform(0.2, 0.95, 1)[0]
            responseTime = np.random.normal(0.5, 0.4, 1)[0]
            availability = np.random.uniform(0.9, 0.99, 1)[0]
            reliability = np.random.uniform(0.7, 0.95, 1)[0]
            s.append(cloud.Service(i, responseTime, reliability, availability, price, matching=1))
        candidates.append(s)
    return candidates


def test(num_act, num_candidates, constraints, weightList):
    rootAct = 1
    x = str((num_act, num_candidates))
    y = []
    z = []

    actGraph = generateActGraph(num_act)

    print("Generating random candidates for {} ...".format(x))

    candidates = generateCandidates(num_act, num_candidates)

    print("Done !")

    # minQos and maxQos definition

    print("Generating global minQos and global maxQos ...")

    minQos, maxQos = minMaxQos(rootAct, num_act, actGraph)

    print('Done')

    # optimal fitness
    l = []

    for i in range(1, 10):
        print("Finding Optimal {} %".format(i * 15), end="\r")
        s = hybrid.ABCgenetic(rootAct, actGraph, candidates, WBee=100, OBee=100, SBee=100, SQ=5 * i, MCN=100 * i, SN=100,
                              p=0.5, minQos=minQos, maxQos=maxQos, constraints=constraints, weightList=weightList)
        l.append(s)

    opt = max(l)
    print('\nDone !')

    # Algorithm execution

    for i in range(10):
        print("Executing Algorithm ({}/10)".format(i + 1), end="\r")
        start_time = time.time()
        fit = hybrid.ABCgenetic(rootAct, actGraph, candidates, WBee=50, OBee=50, SBee=100, SQ=20, MCN=100, SN=50, p=0.5,
                                minQos=minQos, maxQos=maxQos, constraints=constraints, weightList=weightList)
        z.append(time.time() - start_time)
        y.append(fit)

    y = sum(y) / 10
    z = sum(z) / 10

    with open('dataset.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(
            ['50', '50', '50', str(num_act), str(num_candidates), '10', '10', '100', '50', str(y), str(opt),
             str(y / opt)])
        file_writer.writerow('')

    print('\nDone !')

    return x, y / opt, z


# main
constraints = {'responseTime': 1, 'price': 10, 'availability': 0.009, 'reliability': 0.009}
weightList = [0.25, 0.25, 0.25, 0.25]
X, Y, Z = [], [], []  # Y for optimality , Z for scalability
# client input de maniere rapide pour tester
res = test(5, 50, constraints, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(10, 100, constraints, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(10, 100, constraints, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(20, 150, constraints, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(20, 150, constraints, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(30, 200, constraints, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(30, 200, constraints, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])

fig, sub = plt.subplots(1, 2)

# optimality figure

sub[0].set(xlabel="Test variables", ylabel="Normalized fitness values")
sub[0].set_xlim([0, 4])
sub[0].set_ylim([0, 1.5])
sub[0].set_title("Optimality plot")
sub[0].plot(X, Y, "ro-")

# Scalability figure

sub[1].set(xlabel="Test variables", ylabel="Response Time")
sub[1].set_xlim([0, 4])
sub[1].set_ylim([0, 6])
sub[1].set_title("Scalability plot")
sub[1].plot(X, Z, "bo-")

for ax in fig.axes:
    plt.sca(ax)
    plt.xticks(rotation=90)

fig.tight_layout()
plt.show()
