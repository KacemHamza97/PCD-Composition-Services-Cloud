import cloud
from numpy import array , dot
from random import uniform , randint , sample

def verifyConstraints(QosDict,constraints) :
    drt = constraints['responseTime'] - QosDict['responseTime']
    dpr = constraints['price'] - QosDict['price']
    dav = QosDict['availability'] - constraints['availability']
    drel = QosDict['reliability'] - constraints['reliability']

    return drt and dpr and dav and drel


def functions(cp) :   # Objective functions
    QosDict = cp.cpQos()
    f1 = - QosDict["responseTime"]
    f2 = - QosDict["price"]
    f3 = QosDict["availability"] + QosDict["reliability"] + cp.cpMatching()
    return array([f1,f2,f3])


# SQ : condition for scouts , MCN : number of iterations
def algorithm(actGraph, candidates, SQ , MCN,constraints):

    ############################# operations definition ##################################

    def getNeighbor(cp):
        neighbor = cp.clone() # preparing neighbor
        act = randint(0,cp.G.number_of_nodes()-1)
        s = cp.G.nodes[act]["service"] # random service selection
        L = candidates[s.getActivity()] # searching for neighboring service in candidates list
        neighbor.G.nodes[act]["service"] = sorted([neighbor for neighbor in L if neighbor != s], key=lambda x: s.euclideanDist(x))[0]
        return {"cp" : neighbor , "fitness" : fit(neighbor) , "functions" : functions(neighbor) , "limit" : 0 , "probability" : 0}


    def fit(cp):
        dom = 1
        F = functions(cp)
        for i in range(SN) :
            G = functions(solutionsList[i]["cp"])
            if (F >= G).all() and (F > G).any() :   # Domination condition F not worse than G and better at least once
                dom += 1
        return dom / SN


    def nonDominatedSort(X) :
        fronts = [[]]
        SList = list()
        NList = list()
        for p in range(len(X)) :
            Sp = list()
            Np = 0
            F = X[p]["functions"]
            for q in range(len(X)) :
                G = X[q]["functions"]
                if q != p and (F >= G).all() and (F > G).any() :
                    Sp.append(q)
                elif q != p and (G >= F).all() and (G > F).any() :
                    Np += 1
            if Np == 0 :
                fronts[0].append(p)
            SList.append(Sp)
            NList.append(Np)

        i = 0
        while len(fronts[i]) != 0 :
            f = []
            for p in fronts[i] :
                for q in SList[p] :
                    NList[q] -= 1
                    if NList[q] == 0 :
                        f.append(q)
            i += 1
            fronts.append(f)

        return [[X[p] for p in f] for f in fronts]


    def crowdingSort(front) :
        scoresList = list()
        for p in front :
            score = list()
            for f in range(3) :
                high = []
                low = []
                for q in front :
                    if q["functions"][f] < p["functions"][f]  :
                        low.append(q["functions"][f])
                    if q["functions"][f] > p["functions"][f] :
                        high.append(q["functions"][f])
                if len(high) == 0 :
                    next_high = p["functions"][f]
                else :
                    next_high = min(high)
                if len(low) == 0 :
                     next_low = p["functions"][f]
                else :
                    next_low = max(low)
                score.append(next_high-next_low)
            scoresList.append(sum(score))

        return [i[1] for i in sorted(zip(scoresList , front) , key = lambda x:x[0] , reverse = True)]


    def updateSolutions(solutionsList , fronts) :
        i = 0
        S = []

        while i < len(fronts) and len(fronts[i]) <= SN - len(S) :
            S += fronts[i]
            i += 1

        if i < len(fronts) :
            crowding_selection = crowdingSort(fronts[i])[0:SN - len(S)]
            S += crowding_selection

        for cp in S :
            if cp in solutionsList :
                cp["limit"] += 1

        solutionsList[:] = S

        for cp in solutionsList :
            cp["fitness"] = fit(cp["cp"])




    ############################# Algorithm start  ##################################

    # initializing parameters

    SN = 20           # SN : number of ressources

    # solutions  initializing
    solutionsList = list()


    for i in range(SN):
        while 1:
            cp = cloud.CompositionPlan(actGraph, candidates)
            QosDict = cp.cpQos()
            if verifyConstraints(QosDict,constraints) :
                solutionsList.append({"cp" : cp , "fitness" : 0 , "functions" : functions(cp) , "limit" : 0 , "probability" : 0})
                break

    # initializing fitnessList
    for i in range(SN) :
        solutionsList[i]["fitness"] = fit(solutionsList[i]["cp"])


    # Algorithm
    for itera in range(MCN):
        print(f"completed = {(itera+1) * 100 / MCN } %",end = '\r')
        # employed bees phase
        U = list()
        U[:] = solutionsList
        for i in range(SN) :
            cp = solutionsList[i]
            while 1 :
                new = getNeighbor(cp["cp"])
                if verifyConstraints(new["cp"].cpQos(),constraints) :
                    break
            U.append(new)
        # end of employed bees phase
        fronts = nonDominatedSort(U)
        updateSolutions(solutionsList , fronts)
        # Probability update
        s = sum([solutionsList[i]["fitness"] for i in range(SN)])
        for i in range(SN) :
            solutionsList[i]["probability"] = solutionsList[i]["fitness"] / s
        # onlooker bees phase
        U = list()
        U[:] = solutionsList
        s = 0
        t = 0
        while t < SN :
            if solutionsList[s]["probability"] <= uniform(min([solutionsList[x]["probability"] for x in range(SN)]) , max([solutionsList[x]["probability"] for x in range(SN)])) :
                t += 1
                cp = solutionsList[s]
                while 1 :
                    new = getNeighbor(cp["cp"])
                    if verifyConstraints(new["cp"].cpQos(),constraints) :
                        break
                U.append(new)
            s = (s+1) % (SN - 1)
        # end of onlooker bees phase
        fronts = nonDominatedSort(U)
        updateSolutions(solutionsList , fronts)
        # scout bees phase
        scout_targets = []
        for i in range(len(solutionsList)) :
            if solutionsList[i] not in fronts[0] :
                scout_targets.append(i)

        if scout_targets != [] :
            pick = sorted(scout_targets,key = lambda x:solutionsList[x]["limit"])[-1]
            if solutionsList[pick]["limit"] >= SQ :
                while 1 :
                    cp = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
                    if verifyConstraints(cp["cp"].cpQos(),constraints) :
                        solutionsList[pick] = {"cp" : cp , "fitness" : fit(cp) , "functions" : functions(cp) , "limit" : 0 , "probability" : 0}
                        break
        # end of scout bees phase
    # end of algorithm
    print("\n")
    return fronts
