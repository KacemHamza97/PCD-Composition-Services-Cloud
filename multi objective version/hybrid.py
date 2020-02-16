import cloud
from numpy import array , dot
from random import random , randint , sample

def verifyConstraints(QosDict) :
    drt = constraints['responseTime'] - QosDict['responseTime']
    dpr = constraints['price'] - QosDict['price']
    dav = QosDict['availability'] - constraints['availability']
    drel = QosDict['reliability'] - constraints['reliability']

    return drt and dpr and dav and drel

def fit(cp):
    dom = 0
    F = np.array(list(cp.cpQos().values())+[cp.cpMatching()])
    for i in range(SN) :
        G = np.array(list(solutionsList[i].cpQos().values())+solutionsList[i].cpMatching())
        if (F >= G).all() and (F > G).any() :
            dom += 1
    return dom / SN

def BSG(cp1, cp2):

    # Crossover

    # First neighbor

    neighbor1 = new_cp = cp1.clone()

    while 1 :
        x1 = randint(0,cp2.actNum-2)
        x2 = randint(x1+1,cp2.actNum-1)
        for act in list(cp2.G.nodes)[x1,x2+1]:  # Selecting service to replace
                # replacing with service from second parent
                neighbor1.G.nodes[act]["service"] = cp2.G.nodes[act]["service"]
                if verifyConstraints(neighbor1.cpQos()) :
                    break

    # Second neighbor

    neighbor2 = new_cp = cp2.clone()

    while 1 :
        x1 = randint(0,cp1.actNum-2)
        x2 = randint(x1+1,cp1.actNum-1)
        for act in list(cp1.G.nodes)[x1,x2+1]:  # Selecting service to replace
                # replacing with service from second parent
                neighbor2.G.nodes[act]["service"] = cp1.G.nodes[act]["service"]
                if verifyConstraints(neighbor2.cpQos()) :
                    break

    # Mutation

    # First neighbor

    neighbor3 = new_cp = cp1.clone()

    # choose randomly a service to mutate
    service = neighbor3.G.nodes[randint(0, neighbor3.actNum - 1)]["service"]
    while 1 :
        new = sample(candidates[service.getActivity()],1)[0]
        # mutation operation
        neighbor3.G.nodes[new.getActivity()]["service"] = new
        if verifyConstraints(neighbor3.cpQos()) :
            break

    # Second neighbor

    neighbor4 = new_cp = cp2.clone()

    # choose randomly a service to mutate
    service = neighbor4.G.nodes[randint(0, neighbor4.actNum - 1)]["service"]
    while 1 :
        new = sample(candidates[service.getActivity()],1)[0]
        # mutation operation
        neighbor4.G.nodes[new.getActivity()]["service"] = new
        if verifyConstraints(neighbor4.cpQos()) :
            break

    return [neighbor1 , neighbor2 , neighbor3 , neighbor4]


# SQ : condition for scouts , MCN : number of iterations
def ABCgenetic(actGraph, candidates, SQ, MCN,constraints):

    ############################# operations definition ##################################

    def nonDominatedSort(X) :
        fronts = [[]]
        SList = list()
        NList = list()
        for p in range(len(X)) :
            Sp = set()
            Np = 0
            F = functionsList[p]
            for q in range(len(X)) :
                G = functionsList[q]
                if q != pos and (F >= G).all() and (F > G).any() :
                    Sp.add(q)
                else if q != pos and (G >= F).all() and (G > F).any() :
                    Np += 1
            if Np == 0 :
                fronts[0].append(p)
            SList.append(Sp)
            NList.append(Np)

        i = 0
        while len(fronts[i]) == 0 :
            Q = []
            for p in fronts[i] :
                for q in SList[p] :
                    NList[q] -= NList[q] - 1
                    if NList[q] == 0 :
                        Q.append(q)
            i += 1
            fronts.append(Q)

        return [[solutionsList[x] for x in f] for f in fronts]



    def crowdingSort(front) :
        for p in front :
            F = functionsList[p]
            # not complete

    def updateSolutions() :
        i = 0
        S = []
        F = []
        while len(fronts[i]) <= SN :
            for p in fronts[i] :
                S.append(solutionsList[p])
                F.append(functionsList[p])
                if len(S) == SN :
                    solutionsList = S
                    functionsList = F
            i += 1

        L = crowdingSort(fronts[i])
        S += [solutionsList[p] for p in L]
        F += [functionsList[p] for p in L]
        solutionsList = S
        functionsList = F


    ############################# Algorithm start  ##################################

    # initializing parameters

    SN = 20           # SN : number of ressources
    SCP = 4 * MCN / 5  # changing point for scouts


    # solutions ,probability and functions initializing
    solutionsList = list()
    fitnessList = list()
    functionsList = list()
    probabilityList = list(0 for i in range(SN))
    limit = list(0 for i in range(SN))

    for i in range(SN):
        while 1:
            cp = cloud.CompositionPlan(actGraph, candidates)
            QosDict = cp.cpQos()
            if verifyConstraints(QosDict) :
                solutionsList[i].append(cp)
                functionsList[i].append(multi_f(QosDict))
                break

    # initializing fitnessList
    for i in range(SN) :
        fitnessList[i] = fitnessCalc(i)


    # Algorithm
    for itera in range(MCN):
        # employed bees phase
        exploited = sample(list(range(SN)),SN // 2)   # Generating positions list for exploitation
        for i in exploited :
            cp1 = solutionsList[i]
            cp2 = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
            neighbors , QosList = BSG(cp1, cp2) # BSG
            solutionsList += neighborsList
            functionsList += [multi_f(QosDict) for QosDict in QosList]
        # end of employed bees phase
        fronts = nonDominatedSort(solutionsList)
        updateSolutions()
        # Probability update
        for i in exploited :
            s = sum(fitnessList)
            probabilityList[i] = fitnessList[i] / s

        # onlooker bees phase
        # end of onlooker bees phase

        # scout bees phase
        # end of scout bees phase

    # end of algorithm
