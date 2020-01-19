import cloud
import hybrid
import numpy as np
import time
import matplotlib.pyplot as plt
import csv


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


def test(num_act, num_candidates, constraints, weightList):

    x = str((num_act, num_candidates))
    y = []
    z = []

    actGraph = generateActGraph(num_act)

    print("Generating random candidates for {} ...".format(x))

    candidates = generateCandidates(num_act, num_candidates)

    print("Done !")

    # minQos and maxQos definition

    print("Generating global minQos and global maxQos ...")

    minQos, maxQos = minMaxQos(num_act, actGraph)

    print('Done')

    optimal fitness
    rt = 1
    pr = 1
    av = 1
    rel = 1
    vect1 = np.array([rt, pr, av, rel])
    vect2 = np.array(weightList)
    opt = np.dot(vect1, vect2) + 1 #Optimal Qos + matching


    # Algorithm execution

    for i in range(10):
        print("Executing Algorithm ({}/10)".format(i + 1), end="\r")
        start_time = time.time()
        _ , fit = hybrid.ABCgenetic(actGraph, candidates, workers=50, onlookers=50, scouts=50, SQ=10, MCN=100, SN=100, minQos=minQos, maxQos=maxQos, constraints=constraints, weightList=weightList)
        z.append(time.time() - start_time)
        y.append(fit)

    y = sum(y) / 10
    z = sum(z) / 10

    with open('dataset.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([str(num_act), str(num_candidates), '10','50', '50', '50', '10', '100', '100', str(y), str(opt), str(y / opt) ,z])
        file_writer.writerow("")

    print('\nDone !')
    return x, y / opt, z


# main
constraints = {'responseTime': 10, 'price': 1000, 'availability': 10, 'reliability': 10}
weightList = [0.25, 0.25, 0.25, 0.25]
X, Y, Z = [], [], []  # Y for optimality , Z for scalability

res = test(5 , 50 , constraints, weightList)
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
sub[1].set_ylim([0, 10])
sub[1].set_title("Scalability plot")
sub[1].plot(X, Z, "bo-")

for ax in fig.axes:
    plt.sca(ax)
    plt.xticks(rotation=90)

fig.tight_layout()
plt.show()
