import cloud
from numpy import array , dot
from random import uniform , randint , sample

def verifyConstraints(QosDict,constraints) :
    drt = constraints['responseTime'] - QosDict['responseTime']
    dpr = constraints['price'] - QosDict['price']
    dav = QosDict['availability'] - constraints['availability']
    drel = QosDict['reliability'] - constraints['reliability']

    return drt and dpr and dav and drel


def functions(cp) :
    return np.array(list(cp.cpQos().values())+[cp.cpMatching()])

def BSG(cp1, cp2):

    # Crossover

    # First neighbor

    neighbor1 = cp1.clone()

    while 1 :
        x1 = randint(0,cp2.actNum-2)
        x2 = randint(x1+1,cp2.actNum-1)
        for act in list(cp2.G.nodes)[x1:x2+1]:  # Selecting service to replace
                # replacing with service from second parent
                neighbor1.G.nodes[act]["service"] = cp2.G.nodes[act]["service"]
                if verifyConstraints(neighbor1.cpQos()) :
                    break

    # Second neighbor

    neighbor2 = cp2.clone()

    while 1 :
        x1 = randint(0,cp1.actNum-2)
        x2 = randint(x1+1,cp1.actNum-1)
        for act in list(cp1.G.nodes)[x1:x2+1]:  # Selecting service to replace
                # replacing with service from second parent
                neighbor2.G.nodes[act]["service"] = cp1.G.nodes[act]["service"]
                if verifyConstraints(neighbor2.cpQos()) :
                    break

    # Mutation

    # First neighbor

    neighbor3 = cp1.clone()

    # choose randomly a service to mutate
    service = neighbor3.G.nodes[randint(0, neighbor3.actNum - 1)]["service"]
    while 1 :
        new = sample(candidates[service.getActivity()],1)[0]
        # mutation operation
        neighbor3.G.nodes[new.getActivity()]["service"] = new
        if verifyConstraints(neighbor3.cpQos()) :
            break

    # Second neighbor

    neighbor4 = cp2.clone()

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

    def fit(cp):
        dom = 0
        F = functions(cp)
        for i in range(SN) :
            G = functions(solutionsList[i]["cp"])
            if (F >= G).all() and (F > G).any() :
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
        for p in front :
            F = functionsList[p]
            # not complete

    def updateSolutions() :
        i = 0
        S = []
        while len(fronts[i]) <= SN - len(S) :
            S += fronts[i]
            i += 1

        crowding_selection = crowdingSort(fronts[i])
        S += crowding_selection
        for cp in S :
            if cp in solutionsList :
                cp["limit"] += 1

        solutionsList = S
        for cp in S :
            cp["fitness"] = fit(cp)




    ############################# Algorithm start  ##################################

    # initializing parameters

    SN = 20           # SN : number of ressources
    SCP = 4 * MCN / 5  # changing point for scouts


    # solutions  initializing
    solutionsList = list()

    for i in range(SN):
        while 1:
            cp = cloud.CompositionPlan(actGraph, candidates)
            QosDict = cp.cpQos()
            if verifyConstraints(QosDict,constraints) :
                solutionsList[i].append({"cp" : cp , "fitness" : None , "functions" : functions(cp) , "limit" : 0 , "probability" : 0})
                break

    # initializing fitnessList
    for i in range(SN) :
        solutionsList[i]["fitness"] = fit(i)


    # Algorithm
    for itera in range(MCN):
        # employed bees phase
        exploited = sample(list(range(SN)),SN // 2)   # Generating positions list for exploitation
        for i in exploited :
            cp1 = solutionsList[i]["cp"]
            cp2 = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
            neighbors = BSG(cp1, cp2) # BSG
            solutionsList += neighborsList
        # end of employed bees phase
        fronts = nonDominatedSort(solutionsList)
        updateSolutions()
        # Probability update
        s = sum([solutionsList[j]["fitness"] for j in range(SN))
        for i in exploited :
            solutionsList[i]["probability"] = solutionsList[i]["fitness"] / s

        # onlooker bees phase
        for i in exploited :
            if solutionsList[i]["probability"] > uniform(min([solutionsList[x]["probability"] for x in range(SN)]) , max([solutionsList[x]["probability"] for x in range(SN)])) :
                cp1 = solutionsList[i]["cp"]
                cp2 = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
                neighbors = BSG(cp1, cp2) # BSG
                solutionsList += {"cp" : neighborsList[i] , "fitness" : None , "functions" : functions(neighborsList[i]) , "limit" : 0 , "probability" : 0 for i in range(4)}
        # end of employed bees phase
        fronts = nonDominatedSort(solutionsList)
        updateSolutions()
        # end of onlooker bees phase

        # scout bees phase
        for i in exploited :
            if solutionsList[i]["limit"] == SQ :
                while 1 :
                    cp = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
                    if verifyConstraints(cp.cpQos(),constraints) :
                        solutionsList[i]["cp"] = cp
                        solutionsList[i]["fitness"] = fit(cp)
                        solutionsList[i]["functions"] = functions(cp)
                        solutionsList[i]["limit"] = 0
                        break

        # end of scout bees phase

    # end of algorithm
