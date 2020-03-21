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
def algorithm(actGraph, candidates, MCN,constraints):

    ############################# operations definition ##################################

    def exploit(cp1, cp2 , constraints):

        new = cp1.clone()

        while 1 :
            x1 = randint(0,cp2.G.number_of_nodes()-2)
            x2 = randint(x1+1,cp2.G.number_of_nodes()-1)
            for act in list(cp2.G.nodes)[x1:x2+1]:  # Selecting service to replace
                    # replacing with service from EA solution
                    new.G.nodes[act]["service"] = cp2.G.nodes[act]["service"]
            if verifyConstraints(new.cpQos() , constraints) :
                break

        return {"cp" : new , "fitness" : fit(cp) , "functions" : functions(new)}

    def fit(cp):
        dom = 1
        F = functions(cp)
        for i in range(SN) :
            G = functions(solutionsList[i]["cp"])
            if (F >= G).all() and (F > G).any() :   # Domination condition F not worse than G and better at least once
                dom += 1
        return dom / SN


    def nonDominatedSort(X) :
        pareto = []
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
                pareto.append(p)

        return [X[p] for p in pareto]


    def greedySelection(new , current , i) :
        nonlocal EA , solutionsList
        F = functions(new["cp"])
        G = functions(current["cp"])
        if (F >= G).all() and (F > G).any() :
            k = 1
            for x in EA :
                H = x["functions"]
                if (H == F).all() :
                    k = 0
            if k :
                EA.append(new)
        elif (G >= F).all() and (G > F).any() :
            pass
        else :
            k = 1
            for x in EA :
                H = x["functions"]
                if (H == F).all() :
                    k = 0
            if k :
                EA.append(new)
            if uniform(0,1) < 0.5 :
                solutionsList[i] = new



    def crowdingSort(EA) :
        scoresList = list()
        for p in EA :
            score = list()
            for f in range(3) :
                high = []
                low = []
                for q in EA :
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

        return [i[1] for i in sorted(zip(scoresList , EA) , key = lambda x:x[0] , reverse = True)]




    ############################# Algorithm start  ##################################

    # initializing parameters

    SN = 50           # SN : number of ressources

    # solutions  initializing
    solutionsList = list()


    for i in range(SN):
        while 1:
            cp = cloud.CompositionPlan(actGraph, candidates)
            QosDict = cp.cpQos()
            if verifyConstraints(QosDict,constraints) :
                solutionsList.append({"cp" : cp , "fitness" : 0 , "functions" : functions(cp)})
                break

    # initializing fitnessList
    for i in range(SN) :
        solutionsList[i]["fitness"] = fit(solutionsList[i]["cp"])


    pareto = nonDominatedSort(solutionsList)
    EA = pareto
    # Algorithm
    for itera in range(MCN):
        print(f"completed = {(itera+1) * 100 / MCN } %",end = '\r')
        # onlooker bees phase
        exploited = sample(list(range(SN)),SN // 2)
        for i in exploited :
            cp1 = solutionsList[i]
            cp2 = sample(EA,1)[0]
            new = exploit(cp1["cp"], cp2["cp"] , constraints)
            greedySelection(new,cp1,i)
        # end of onlooker bees phase
        EA = nonDominatedSort(EA)
        if len(EA) > 10 :
            EA = crowdingSort(EA)[:10]
        # end of scout bees phase
    # end of algorithm
    print("\n")

    return EA
