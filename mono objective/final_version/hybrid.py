import cloud
from numpy import array , dot
from random import random , randint , sample , uniform
from math import inf

# returning the nearest neighbor of service based on euclidean distance
def getNeighbor(service , candidates):
    return min([neighbor for neighbor in candidates if neighbor != service], key=lambda x: service.euclideanDist(x))

def verifyConstraints(qos , constraints) :
    drt = constraints['responseTime'] - qos['responseTime']
    dpr = constraints['price'] - qos['price']
    dav = qos['availability'] - constraints['availability']
    drel = qos['reliability'] - constraints['reliability']

    return drt and dpr and dav and drel

# Objective function
def fit(cp, minQos , maxQos , weights):
    qos = cp.cpQos()
    rt = (maxQos['responseTime'] - qos['responseTime']) / (maxQos['responseTime'] - minQos['responseTime'])
    pr = (maxQos['price'] - qos['price']) / (maxQos['price'] - minQos['price'])
    av = (qos['availability'] - minQos['availability']) / (maxQos['availability'] - minQos['availability'])
    rel = (qos['reliability'] - minQos['reliability']) / (maxQos['reliability'] - minQos['reliability'])
    # vectorial product
    return dot(array([rt, pr, av, rel]), weights)

# Mutation
def mutate(cp, new_service):
    new_cp = cp.clone()
    # new_service is added to the composition plan
    new_cp.G.nodes[new_service.getActivity()]["service"] = new_service
    return(new_cp)


# Crossover
def crossover(parent1, parent2):
    child = parent1.clone()    # creating new child identical to first parent
    # modifying child
    for act in child.G.nodes:  # Selecting service to replace
        if random() <= 0.2:  # 20 % chance of crossover
            # replacing with service from second parent
            child.G.nodes[act]["service"] = parent2.G.nodes[act]["service"]
    return child

# SQ : condition for scouts , MCN : number of iterations
def ABCgenetic(actGraph, candidates,SN,SQ,MCN,constraints, weights):

    def updateBest(fit = None) :
        nonlocal best_fit , best_cp
        if fit == None :        # No parameters passed
            fit = max(fitnessList)

        if  fit > best_fit :
            best_fit = fit      # Updating best fitness
            best_cp = solutionsList[fitnessList.index(fit)]   # Updating best solution


    def updateMinMax() :
        nonlocal best_fit , fitnessList , minQos , maxQos
        # updating minQos and maxQos
        # looking for minQos and maxQos in best_Qos
        try :
            for qos in best_Qos :
                if best_Qos[qos] < minQos[qos] :
                    minQos[qos] = best_Qos[qos]
                if best_Qos[qos] > maxQos[qos] :
                    maxQos[qos] = best_Qos[qos]
        except : # best_Qos not created
            None
        # looking for minQos and maxQos in solutionsList
        for cp in solutionsList :
            qosDict = cp.cpQos()
            for qos in qosDict :
                if qosDict[qos] < minQos[qos] :
                    minQos[qos] = qosDict[qos]
                if qosDict[qos] > maxQos[qos] :
                    maxQos[qos] = qosDict[qos]
        # Updating best fitness
        try :
            best_fit = fit(best_cp, minQos , maxQos , weights)
        except : # best_cp not created
            None
        # updating fitnessList
        for i in range(SN) :
            fitnessList[i] = fit(solutionsList[i], minQos , maxQos , weights)


    ############################# Algorithm start  ##################################

    # initializing parameters

    SCP = 9 * MCN / 10  # changing point for scouts


    # solutions and fitness initializing
    solutionsList = list()
    fitnessList = list(0 for i in range(SN))
    probabilityList = list(0 for i in range(SN))
    minQos = {'responseTime': inf,'price' : inf,'availability' : inf,'reliability' : inf}
    maxQos = {'responseTime': 0,'price' : 0,'availability' : 0,'reliability' : 0}
    limit = list(0 for i in range(SN))

    for i in range(SN):
        while 1:
            cp = cloud.CompositionPlan(actGraph, candidates)
            if verifyConstraints(cp.cpQos(), constraints):
                solutionsList.append(cp)
                break


    #minQos maxQos and fitnessList initializing
    updateMinMax()

    # initializing best_fit and best_cp
    best_fit = max(fitnessList)
    best_cp =  solutionsList[fitnessList.index(best_fit)]
    # Algorithm
    for itera in range(MCN):
        # employed bees phase
        exploited = sample(list(range(SN)),SN // 2)   # Generating positions list for exploitation
        for i in exploited :
            cp1 = solutionsList[i]
            while 1 :
                cp2 = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
                child = crossover(cp1, cp2) # Crossover operation
                if verifyConstraints(child.cpQos(), constraints):
                    new_fitness = fit(child, minQos , maxQos , weights)
                    if new_fitness > fitnessList[i]:  # checking if child fitness is better than parent fitness
                        fitnessList[i] = new_fitness
                        solutionsList[i] = child
                        limit[i] = 0
                    else:
                        limit[i] += 1
                    break
        # end of employed bees phase

        updateBest()

        # Probability update
        s = sum(fitnessList)
        for i in exploited :
            probabilityList[i] = fitnessList[i] / s

        # onlooker bees phase
        for i in exploited:
            if probabilityList[i] > uniform(min(probabilityList),max(probabilityList)):
                cp1 = solutionsList[i]
                cp2 = best_cp   # current best
                while 1 :
                    child = crossover(cp1, cp2) # Crossover operation
                    if verifyConstraints(child.cpQos() , constraints):
                        new_fitness = fit(child ,minQos , maxQos , weights)
                        if new_fitness > fitnessList[i]:    # checking if child fitness is better than parent fitness
                            fitnessList[i] = new_fitness
                            solutionsList[i] = child
                            limit[i] = 0
                            updateBest(new_fitness)
                        else:
                            limit[i] += 1
                        break
        # end of onlooker bees phase

        # scout bees phase
        for i in exploited:
            if limit[i] >= SQ:  # verifying scouts condition
                if itera >= SCP: # change of scouts behaviour condition to mutating
                    cp = solutionsList[i]
                    while 1:
                        # choose randomly a service to mutate
                        service = cp.G.nodes[randint(0, cp.G.number_of_nodes() - 1)]["service"]
                        neighborsList = candidates[service.getActivity()]
                        neighbor = getNeighbor(service,neighborsList)
                        # mutation operation
                        new = mutate(cp,neighbor)
                        if verifyConstraints(new.cpQos(), constraints):
                            solutionsList[i] = new
                            fitnessList[i] = fit(new ,minQos , maxQos , weights)
                            break

                else:   # searching for new ressources to exploit
                    while 1:
                        cp = cloud.CompositionPlan(actGraph, candidates)
                        if verifyConstraints(cp.cpQos(), constraints) :
                            solutionsList[i] = cp
                            fitnessList[i] = fit(cp , minQos , maxQos , weights)
                            break

                limit[i] = 0
        # end of scout bees phase
        updateMinMax()

    # end of algorithm
    return best_cp
