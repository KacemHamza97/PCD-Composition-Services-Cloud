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
def ABCgenetic(actGraph, candidates, SQ, MCN,constraints):

    ############################# operations definition ##################################

    def BSG(cp1, cp2 , constraints):

        # Crossover

        # First neighbor

        neighbor1 = cp1.clone()

        while 1 :
            x1 = randint(0,cp2.G.number_of_nodes()-2)
            x2 = randint(x1+1,cp2.G.number_of_nodes()-1)
            for act in list(cp2.G.nodes)[x1:x2+1]:  # Selecting service to replace
                    # replacing with service from second parent
                    neighbor1.G.nodes[act]["service"] = cp2.G.nodes[act]["service"]
            if verifyConstraints(neighbor1.cpQos() , constraints) :
                break

        # Second neighbor

        neighbor2 = cp2.clone()

        while 1 :
            x1 = randint(0,cp1.G.number_of_nodes()-2)
            x2 = randint(x1+1,cp1.G.number_of_nodes()-1)
            for act in list(cp1.G.nodes)[x1:x2+1]:  # Selecting service to replace
                    # replacing with service from second parent
                    neighbor2.G.nodes[act]["service"] = cp1.G.nodes[act]["service"]
            if verifyConstraints(neighbor2.cpQos() , constraints) :
                break

        # Mutation

        # First neighbor

        neighbor3 = cp1.clone()

        # choose randomly a service to mutate
        service = neighbor3.G.nodes[randint(0, neighbor3.G.number_of_nodes() - 1)]["service"]
        while 1 :
            new = sample(candidates[service.getActivity()],1)[0]
            # mutation operation
            neighbor3.G.nodes[new.getActivity()]["service"] = new
            if verifyConstraints(neighbor3.cpQos() , constraints) :
                break

        # Second neighbor

        neighbor4 = cp2.clone()

        # choose randomly a service to mutate
        service = neighbor4.G.nodes[randint(0, neighbor4.G.number_of_nodes() - 1)]["service"]
        while 1 :
            new = sample(candidates[service.getActivity()],1)[0]
            # mutation operation
            neighbor4.G.nodes[new.getActivity()]["service"] = new
            if verifyConstraints(neighbor4.cpQos() , constraints) :
                break

        neighborsList = [neighbor1 , neighbor2 , neighbor3 , neighbor4]
        return [{"cp" : cp , "fitness" : None , "functions" : functions(cp) , "limit" : 0 , "probability" : 0} for cp in neighborsList]

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
        exploited = sample(list(range(SN)),SN // 2)   # Generating positions list for exploitation
        U = list()
        U[:] = solutionsList
        for i in exploited :
            cp1 = solutionsList[i]["cp"]
            cp2 = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
            neighbors = BSG(cp1, cp2 , constraints) # BSG
            U += neighbors
        # end of employed bees phase
        fronts = nonDominatedSort(U)
        updateSolutions(solutionsList , fronts)
        # Probability update
        s = sum([solutionsList[i]["fitness"] for i in range(SN)])
        for i in exploited :
            solutionsList[i]["probability"] = solutionsList[i]["fitness"] / s

        # onlooker bees phase
        U = list()
        U[:] = solutionsList
        for i in exploited :
            if solutionsList[i]["probability"] > uniform(min([solutionsList[x]["probability"] for x in range(SN)]) , max([solutionsList[x]["probability"] for x in range(SN)])) :
                cp1 = solutionsList[i]["cp"]
                cp2 = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
                neighbors = BSG(cp1, cp2 , constraints) # BSG
                U += neighbors
        # end of employed bees phase
        fronts = nonDominatedSort(solutionsList)
        updateSolutions(solutionsList , fronts)
        # end of onlooker bees phase

        # scout bees phase
        update = 0
        U = list()
        U[:] = solutionsList
        for i in exploited :
            if solutionsList[i]["limit"] == SQ :
                while 1 :
                    cp = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
                    if verifyConstraints(cp.cpQos(),constraints) :
                        U.append({"cp" : cp , "fitness" : fit(cp) , "functions" : functions(cp) , "limit" : 0 , "probability" : 0})
                        break
                update = 1
        # end of scout bees phase
        if update :
            fronts = nonDominatedSort(U)
            updateSolutions(solutionsList , fronts)

    # end of algorithm
    print("\n")
    return array([sol["functions"] for sol in solutionsList]) , array([sol["functions"] for sol in fronts[0]])
