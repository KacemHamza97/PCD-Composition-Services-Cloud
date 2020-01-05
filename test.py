import cloud
import hybrid
import numpy as np
import time
import matplotlib.pyplot as plt


def minMaxQos(listQos, minQos, maxQos):
    for j in ['responseTime', 'price', 'availability', 'reliability']:
        minQos[j] = min(i[j] for i in listQos)
        maxQos[j] = max(i[j] for i in listQos)


def updateListQos(compositionPlan, listQos, minQos, maxQos):
    k = [compositionPlan.evaluateResponseTime(), compositionPlan.evaluatePrice(),
         compositionPlan.evaluateAvailability(), compositionPlan.evaluateReliability()]
    L = ['responseTime', 'price', 'availability', 'reliability']
    d = {i: j for i, j in zip(L, k)}
    listQos.append(d)


def generateActGraph(num_act):
    return ([[i, i + 1, 0] for i in range(1, num_act)])


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
    return (candidates)


def test(num_act, num_candidates, weightList):
    rootAct = 1
    x = str((num_act, num_candidates))
    y = []
    z = []

    actGraph = generateActGraph(num_act)

    print("Generating random candidates for {} ...".format(x))

    candidates = generateCandidates(num_act, num_candidates)

    print("Done !")

    # minQos and maxQos definition

    minQos = {}

    maxQos = {}

    print("Generating global minQos and global maxQos ...")
    listQos = []
    for i in range(10):
        c = cloud.randomCompositionPlan(rootAct, actGraph, candidates)
        updateListQos(c, listQos, minQos, maxQos)
    minMaxQos(listQos, minQos, maxQos)

    print("Done !")

    # optimal fitness
    l = []

    for i in range(1, 6):
        print("Finding Optimal solution takes a moment ({} %)".format(i * 10), end="\r")
        s = hybrid.ABCgenetic(rootAct, actGraph, candidates, SQ=50 * i, MCN=500 * i, SN=100, p=0.5, minQos=minQos, maxQos=maxQos, weightList=weightList)
        l.append(s)

    opt = max(l)

    print("\nDone !")

    # Algorithm execution

    for i in range(20):
        print("Executing Algorithm ({}/30)".format(i + 1), end="\r")
        start_time = time.time()
        fit = hybrid.ABCgenetic(rootAct, actGraph, candidates, SQ=10, MCN=100, SN=50, p=0.5, minQos=minQos, maxQos=maxQos, weightList=weightList)
        z.append(time.time() - start_time)
        y.append(fit)
    y = sum(y) / 20
    z = sum(z) / 20

    print("\nDone !")

    return x, y / opt, z


# main

weightList = [0.25, 0.25, 0.25, 0.25]
X, Y, Z = [], [], []  # Y for optimality , Z for scalability
res = test(5, 50, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(10, 100, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(10, 100, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(20, 150, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(20, 150, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(30, 200, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])
res = test(30, 200, weightList)
X.append(res[0])
Y.append(res[1])
Z.append(res[2])

fig, sub = plt.subplots(1, 2)

# optimality figure

sub[0].set(xlabel="Test variables", ylabel="Normalized fitness values")
sub[0].set_xlim([0, 4])
sub[0].set_ylim([0.9, 1.01])
sub[0].set_title("Optimality plot")
sub[0].plot(X, Y, "ro-")

# Scalability figure

sub[1].set(xlabel="Test variables", ylabel="Response Time")
sub[1].set_xlim([0, 4])
sub[1].set_ylim([0, 7])
sub[1].set_title("Scalability plot")
sub[1].plot(X, Z, "bo-")

for ax in fig.axes:
    plt.sca(ax)
    plt.xticks(rotation=90)

fig.tight_layout()
plt.show()
