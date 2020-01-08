import cloud
import hybrid
import numpy as np
import time
import matplotlib.pyplot as plt
import csv


def minMaxQos(listQos):
    minQos , maxQos = {} , {}
    for j in ['responseTime', 'price', 'availability', 'reliability']:
        minQos[j] = min(i[j] for i in listQos)
        maxQos[j] = max(i[j] for i in listQos)
    return(minQos , maxQos)


def updateListQos(compositionPlan , listQos):
    k = [compositionPlan.evaluateResponseTime(), compositionPlan.evaluatePrice(),
         compositionPlan.evaluateAvailability(), compositionPlan.evaluateReliability()]
    L = ['responseTime', 'price', 'availability', 'reliability']
    d = {i: j for i, j in zip(L, k)}
    listQos.append(d)


def generateActGraph(num_act):       # Sequential
    return [[i, i + 1, 0] for i in range(num_act - 1)]


def generateCandidates(num_act, num_candidates):
    candidates = []
    for i in range(num_act):
        s = []
        for j in range(num_candidates):
            price = np.random.uniform(0.2, 0.95, 1)[0]
            responseTime = np.random.normal(0.5, 0.4, 1)[0]
            availability = np.random.uniform(0.9, 0.99, 1)[0]
            reliability = np.random.uniform(0.7, 0.95, 1)[0]
            s.append(cloud.Service(i, responseTime, reliability, availability, price, matching=1))
        candidates.append(s)
    return candidates


def test(num_act, num_candidates, weightList):

    x = str((num_act, num_candidates))
    y = []
    z = []

    actGraph = generateActGraph(num_act)

    print("Generating random candidates for {} ...".format(x))

    candidates = generateCandidates(num_act, num_candidates)

    print("Done !")

    # minQos and maxQos definition

    print("Generating global minQos and global maxQos ...")

    listQos = []
    for i in range(10) :
        s = cloud.randomCompositionPlan(actGraph, candidates)
        updateListQos(s,listQos)
    minQos , maxQos = minMaxQos(listQos)

    print('Done')

    # optimal fitness
    l = []

    print("Finding Optimal ... ")
    for i in range(1,10):
        s = hybrid.ABCgenetic(actGraph, candidates, WBee=100, OBee=100, SBee=100, SQ=4 + i, MCN=200 * i, SN=100,
                              p=0.5, minQos=minQos, maxQos=maxQos,weightList=weightList)
        l.append(s)

    opt = max(l)
    print('\nDone !')

    # Algorithm execution

    for i in range(10):
        print("Executing Algorithm ({}/10)".format(i + 1), end="\r")
        start_time = time.time()
        fit = hybrid.ABCgenetic(actGraph, candidates, WBee=50, OBee=50, SBee=100, SQ=5, MCN=100, SN=100, p=0.5,
                                minQos=minQos, maxQos=maxQos,weightList=weightList)
        z.append(time.time() - start_time)
        y.append(fit)

    y = sum(y) / 10
    z = sum(z) / 10

    with open('dataset.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([str(num_act), str(num_candidates), '10','50', '50', '100', '5', '100', '100', str(y), str(opt), str(y / opt)])
        file_writer.writerow('')

    print('\nDone !')

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
