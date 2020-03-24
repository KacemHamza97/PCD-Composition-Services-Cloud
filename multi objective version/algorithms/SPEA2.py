import cloud
from numpy import array


def verifyConstraints(QosDict, constraints):
    drt = constraints['responseTime'] - QosDict['responseTime']
    dpr = constraints['price'] - QosDict['price']
    dav = QosDict['availability'] - constraints['availability']
    drel = QosDict['reliability'] - constraints['reliability']

    return drt and dpr and dav and drel  # return true if constraints are respected else false


def functions(cp):
    QosDict = cp.cpQos()
    f1 = - QosDict["responseTime"]
    f2 = - QosDict["price"]
    f3 = QosDict["availability"] + QosDict["reliability"] + cp.cpMatching()
    return array([f1, f2, f3])  # Objective functions


def distance(cp1, cp2):
    QosDict1 = cp1.cpQos()
    QosDict2 = cp2.cpQos()

    f1 = QosDict1["responseTime"] - QosDict2["responseTime"]
    f2 = QosDict1["price"] - QosDict2["price"]
    f3 = (QosDict1["availability"] + QosDict1["reliability"] + cp1.cpMatching()) - (
            QosDict2["availability"] + QosDict2["reliability"] + cp2.cpMatching())
    return (f1 ** 2 + f2 ** 2 + f3 ** 2) ** 0.5  # euclidien distance


def dominates(cp1, cp2):
    F = functions(cp1)
    G = functions(cp2)
    return (F >= G).all() and (F > G).any()  # return true if cp1 dominates cp2 else false


def SPEA2(actGraph, candidates, SQ, MCN, constraints):

    ############################# operations definition ##################################

    def intialize(n, L):
        for i in range(n):
            while 1:
                cp = cloud.CompositionPlan(actGraph, candidates)
                QosDict = cp.cpQos()
                if verifyConstraints(QosDict, constraints):
                    L.append({"cp": cp, "fitness": 0, "functions": functions(cp)})
                    break

    def strength(cp):
        s = 1
        for i in range(len(P + EA)):
            cp2 = (P + EA)[i]["cp"]
            if dominates(cp, cp2):  # Domination condition F not worse than G and better at least once
                s += 1
        return s  # strength of a composition plan

    def rawFitness(cp):
        return sum([strength((EA + P)[i]["cp"]) for i in range(len(P + EA)) if dominates((EA + P)[i]["cp"], cp)])  # rawfitness is to minimize !

    def fit(cp):
        dist = []
        for i in range(len(P + EA)):
            dist.append(distance(cp, (P + EA)[i]["cp"]))
        return 1 / (dist.sort()[k] + 2) + rawFitness(cp)  # fitness of a comosition plan

    def nondominated_individuals(P, EA):
        non_dominated = []
        for i in range(len(P + EA)):
            for j in range(len(P + EA)):
                if dominates((P + EA)[j], (P + EA)[i]):
                    break
            non_dominated.append((P + EA)[i])
        return non_dominated  # liste des dictionnaires chaque dict contient un cp nondominated

    def sort_population_by_fitness(X):
        return sorted(X, key=lambda x: x["fitness"])

    def truncation(n):
        nonlocal EA
        d = []
        e = set()
        for i, d1 in enumerate(EA):
            e.add(i)
            for j, d2 in enumerate(EA):
                if j not in e:  # astuce pour ne pas calculer la distance (d1 , d2) et (d2,d1)
                    d.append((d1, d2, distance(d1["cp"], d2["cp"])))  # tuple (d1,d2,distance)
        d.sort(key=lambda x: x[2]) # sort by distance
        L = []
        for elem in d:
            if len(L) < n and elem[0] not in L and elem[1] not in L: # the 3rd condition : to avoid deleting some thing had been deleted exemple fig 2 page 9
                L.append(elem[1])
        for elem in EA:
            if elem in L:
                EA.remove(elem)

    def update_EA(dominated_individuals):
        nonlocal EA
        if len(EA) < EN:
            EA.extends(sort_population_by_fitness(dominated_individuals)[EN - len(EA)])
        elif len(EA) > EN:
            truncation(len(EA) - EN)

    def binaryTournement():
        pass
    def reconbinition():
        pass

    ############################# Algorithm start  ##################################

    # initializing parameters

    N = 50  # N : Pooulation size
    EN = 10  # EN : archive size
    T = 20  # maximum number of generations
    k = int((EN + N) ** 0.5)  # k-th nearest data point number
    P = list()  # liste des solutions : liste des dictionnaires chaque dict contient un plan de composition + fitness + functions


    # initializing Population and archive
    intialize(N, P)
    EA = []  # archive
    # Algorithm
    for t in range(T):
        for i in range(N):
            P[i]["fitness"] = fit(P[i]["cp"])
        for i in range(len(EA)):
            EA[i]["fitness"] = fit(EA[i]["cp"])

        EA.extend(nondominated_individuals(P, EA))
        dominated_individuals = []
        for d1 in P:  # EAi un dictionnaire
            for d2 in P:
                if dominates(d2["cp"], d1["cp"]):
                    dominated_individuals.append(d1)
                    break

        update_EA(dominated_individuals)
        binaryTournement()
        reconbinition()

    return EA