import cloud
from numpy import array , dot
from random import random , randint , sample

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
    return dot(array([rt, pr, av, rel]), weights) + cp.cpMatching()

# Mutation
def mutate(cp, new):
    # new is added to the composition plan
    cp.G.nodes[new.getActivity()]["service"] = new


# Crossover
def crossover(parent1, parent2):
    child = parent1.clone()    # creating new child identical to first parent
    # modifying child
    for act in child.G.nodes:  # Selecting service to replace
        if randint(0, 1):  # 50 % chance of crossover
            # replacing with service from second parent
            child.G.nodes[act]["service"] = parent2.G.nodes[act]["service"]
    return child

# SQ : condition for scouts , MCN : number of iterations
def ABCgenetic(actGraph, candidates, SQ, MCN,minQos, maxQos, constraints, weights):

    def updateBest(fit = None) :
        nonlocal best_fit , best_cp
        if fit == None :        # No parameters passed
            fit = max(fitnessList)

        if  fit > best_fit :
            best_fit = fit      # Updating best fitness
            best_cp = solutionsList[fitnessList.index(fit)]   # Updating best solution



    ############################# Algorithm start  ##################################

    # initializing parameters

    SN = 20           # SN : number of ressources
    SCP = 4 * MCN / 5  # changing point for scouts


    # solutions and fitness initializing
    solutionsList = list()
    fitnessList = list()
    probabilityList = list(0 for i in range(SN))
    limit = list(0 for i in range(SN))

    for i in range(SN):
        while 1:
            cp = cloud.CompositionPlan(actGraph, candidates)
            if verifyConstraints(cp.cpQos(), constraints):
                solutionsList.append(cp)
                fitnessList.append(fit(cp ,minQos , maxQos , weights))
                break


    # initializing best_fit and best_cp
    best_fit = max(fitnessList)
    best_cp =  solutionsList[fitnessList.index(best_fit)]

    # Algorithm
    for itera in range(MCN):
        print("iteration = {} , best = {}".format(itera+1,best_fit / 2),end = '\r')
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
        for i in exploited :
            s = sum(fitnessList)
            probabilityList[i] = fitnessList[i] / s

        # onlooker bees phase
        for i in exploited:
            if probabilityList[i] > random():
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
            if limit[i] == SQ:  # verifying scouts condition
                if itera >= SCP: # change of scouts behaviour condition to mutating
                    cp = solutionsList[i]
                    while 1:
                        # choose randomly a service to mutate
                        service = cp.G.nodes[randint(0, cp.G.number_of_nodes() - 1)]["service"]
                        neighborsList = candidates[service.getActivity()]
                        neighbor = getNeighbor(service,neighborsList)
                        # mutation operation
                        mutate(cp,neighbor)
                        if verifyConstraints(cp.cpQos(), constraints):
                            fitnessList[i] = fit(cp ,minQos , maxQos , weights)
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


    # end of algorithm
    return best_cp , best_fit
