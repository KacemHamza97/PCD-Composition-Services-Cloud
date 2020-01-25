import cloud
import random


# candidates is a list made of list of services that perform a common activity , each list of services represents an activity
# candidates is indexed based on the attribut activity of each service (cloud.py)
# actGraph is a graph with only activities indexes linked to each other by arcs


# returning the nearest neighbor of service based on euclidean distance

def getNeighbor(service, candidates):
    L = candidates[service.getActivity()]
    return min([neighbor for neighbor in L if neighbor != service], key=lambda x: service.euclideanDist(x))


# Fitness function
def f(cp, minQos, maxQos, constraints, weightList):
    return cp.globalQos(minQos, maxQos, constraints, weightList) + cp.cpMatching()


# SQ : condition for scouts , MCN : termination condition , SN : number of ressources
def ABCgenetic(actGraph, candidates, SQ, MCN, SN, minQos, maxQos, constraints,weightList):
    # initializing
    solutions = list()
    fitnessList = list()
    probabilityList = list(0 for i in range(SN))
    limit = list(0 for i in range(SN))
    CP = 4 * MCN / 5  # changing point for scouts
    # solutions and fitness initializing
    for i in range(SN):
        while 1:
            sol = cloud.CompositionPlan(actGraph, candidates)
            fit = f(sol, minQos, maxQos, constraints, weightList)
            if fit:
                solutions.append(sol)
                fitnessList.append(fit)
                break

    # Algorithm
    for itera in range(1, MCN + 1):

        # employed bees phase
        exploited = []
        for i in range(SN // 2):
            i = random.randint(0, SN - 1)
            exploited.append(i)
            cp1 = solutions[i]
            cp2 = cloud.CompositionPlan(actGraph, candidates) # randomly generated
            # Crossover operation
            child = cloud.crossover(cp1, cp2)
            fit = f(child, minQos, maxQos, constraints, weightList)
            if fit > fitnessList[i]:
                fitnessList[i] = fit
                solutions[i] = child
                limit[i] = 0
            else:
                limit[i] += 1

        # Probability update
        for i in exploited :
            s = sum(fitnessList)
            probabilityList[i] = fitnessList[i] / s

        # finding best solution after employed bees phase
        best_fit = max(fitnessList)
        best_cp = solutions[fitnessList.index(best_fit)]

        # onlooker bees phase
        for i in exploited:
            if probabilityList[i] > random.random():
                cp1 = solutions[i]
                cp2 = best_cp   # current best
                # Crossover operation
                child = cloud.crossover(cp1, cp2)
                fit = f(child, minQos, maxQos, constraints, weightList)
                if fit > fitnessList[i]:
                    fitnessList[i] = fit
                    solutions[i] = child
                    limit[i] = 0
                    if fit > best_fit :       # modifying current best for next bee
                        best_fit = fit
                        best_cp = child
                else:
                    limit[i] += 1

        # scout bees phase
        for i in exploited:
            if limit[i] == SQ:  # scouts bee condition verified
                if itera >= CP:
                    cp = solutions[i]
                    while 1:
                        # choose randomly a service to mutate
                        service = cp.G.nodes[random.randint(0, cp.G.number_of_nodes() - 1)]["service"]
                        # new service index
                        neighbor = getNeighbor(service, candidates)
                        # mutation operation
                        cp.mutate(neighbor)
                        fit = f(cp, minQos, maxQos, constraints, weightList)

                        if fit:
                            solutions[i] = cp
                            fitnessList[i] = fit
                            break

                else:
                    # Scouting
                    while 1:
                        cp = cloud.CompositionPlan(actGraph, candidates)
                        fit = f(sol, minQos, maxQos, constraints, weightList)
                        if fit:
                            solutions[i] = cp
                            fitnessList[i] = f(cp, minQos, maxQos, constraints, weightList)
                            break

                limit[i] = 0

        # the best of each iteration
        best_itera = max(fitnessList)
        if best_itera > best_fit :
            best_cp = solutions[fitnessList.index(best_itera)]
            best_fit = best_itera
    return best_cp , best_fit
