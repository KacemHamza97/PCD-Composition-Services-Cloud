import cloud
import copy
import random


# candidates is a list made of list of services that perform a common activity , each list of services represents an activity
# candidates is indexed based on the attribut activity of each service (cloud.py)
# actGraph is a graph with only activities indexes linked to each other by arcs
# sort neighbors of service based on euclidean distance from the nearest to the furthest

def getNeighbors(s, candidates):  # s is a service
    L = candidates[s.getActivity()]
    return sorted([neighbor for neighbor in L if neighbor != s], key=lambda x: s.euclideanDist(x))


# Fitness function
def f(cp, minQos, maxQos, constraints, weightList):
    return cp.globalQos(minQos, maxQos, constraints, weightList) + cp.cpMatching()


# SQ : condition for scouts , MCN : termination condition , SN : number of compositionPlans , p :probability
def ABCgenetic(actGraph, candidates, workers, onlookers, scouts, SQ, MCN, SN, minQos, maxQos, constraints,weightList):
    # initializing
    solutions = list()
    fitnessList = list()
    probabilityList = list(0 for i in range(SN))
    limit = list(0 for i in range(SN))
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

        # working bees phase
        for bee in range(workers):
            i = random.randint(0, SN - 1)
            cp1 = solutions[i]  # cp is a composition plan
            cp2 = solutions[random.randint(0, SN - 1)]
            # Crossover
            child = cloud.crossover(cp1, cp2)
            Q = f(child, minQos, maxQos, constraints, weightList)
            if Q > fitnessList[i]:
                fitnessList[i] = Q
                solutions[i] = child
                limit[i] = 0
            else:
                limit[i] += 1

        # Probability update
        for i in range(SN):
            s = solutions[i]
            probabilityList[i] = fitnessList[i] / sum(fitnessList)

        # onlooker bees phase
        for bee in range(onlookers):
            i = random.randint(0, SN - 1)
            if probabilityList[i] > random.random():
                cp = solutions[i]  # cp is a composition plan
                # choose randomly a service to mutate
                service = cp.G.nodes[random.randint(0, cp.G.number_of_nodes() - 1)]["service"]
                # new service index
                neighbors = getNeighbors(service, candidates)
                N = len(neighbors)
                # mutation
                if random.random() <= 0.7 :
                    cp.mutate(neighbors[(N - 1) // itera])
                    Q = f(cp, minQos, maxQos, constraints, weightList)
                    if Q > fitnessList[i]:
                        fitnessList[i] = Q
                        limit[i] = 0
                    else:
                        cp.mutate(service)  # mutation reset
                        limit[i] += 1

        # scout bees phase
        for bee in range(scouts):
            i = random.randint(0, SN - 1)
            if limit[i] == SQ:  # scouts bee condition verified
                minIndex = fitnessList.index(min(fitnessList))
                cp = cloud.CompositionPlan(actGraph, candidates)
                solutions[minIndex] = cp
                fitnessList[minIndex] = f(cp, minQos, maxQos, constraints, weightList)
                limit[minIndex] = 0

    best = max(fitnessList)
    return solutions[fitnessList.index(best)] , best
