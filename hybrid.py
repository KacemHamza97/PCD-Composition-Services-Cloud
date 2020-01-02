import cloud
import copy
import random

# candidates is a list made of list of services that perform a common activity , each list of services represents an activity
# candidates is indexed based on the attribut activity of each service (cloud.py)
# actGraph is a graph with only activities indexes linked to each other by arcs
# rootAct is the first activity
# sort neighbors of service based on euclidean distance from the nearest to the furthest

def getNeighbors(s, candidates):  # s is a service
    L = candidates[s.getActivity() - 1]
    return sorted([neighbor for neighbor in L if neighbor != s], key=lambda x: s.euclideanDist(x))


# Fitness function
def f(compositionplan , minQos, maxQos):
    return ( compositionplan.globalQos(minQos, maxQos) + compositionplan.evaluateMatching())


# SQ : condition for scouts , MCN : termination condition , SN : number of compositionPlans , p :probability
def ABCgenetic(rootAct, actGraph, candidates, SQ, MCN, SN, p , minQos , maxQos):
    # initializing
    solutions = list()
    fitnessList = list()
    probabilityList = list(0 for i in range(SN))
    limit = list(0 for i in range(SN))
    CP = 4 * MCN / 5  # changing point for scouts
    # solutions and fitness initializing

    for i in range(SN):
        solutions.append(cloud.randomCompositionPlan(rootAct, actGraph, candidates))

    for i in range(SN):
        fitnessList.append(f(solutions[i],minQos , maxQos))

    # Algorithm
    for itera in range(1, MCN + 1):

        # working bees phase
        for bee_num in range(SN // 2):
            i = random.randint(0,SN-1)
            s = solutions[i]  # s is a workflow
            # choose randomly a service to mutate
            service = s.randomServ()
            # new service index
            neighbors = getNeighbors(service, candidates)
            N = len(neighbors)
            index = (N - 1) // itera
            # mutation
            s.mutate(service, neighbors[index])
            Q = f(s,minQos , maxQos)
            if Q > fitnessList[i]:
                fitnessList[i] = Q
                limit[i] = 0
            else:
                s.mutate(neighbors[index], service)  # mutation reset
                limit[i] += 1

        # Probability update
        for i in range(SN):
            s = solutions[i]
            probabilityList[i] = f(s,minQos , maxQos) / sum(fitnessList)

        # onlooker bees phase
        for bee_num in range(SN // 2):
            i = random.randint(0,SN-1)
            if probabilityList[i] > p:
                s = solutions[i]  # s is a workflow
                # choose randomly a service to mutate
                service = s.randomServ()
                # new service index
                neighbors = getNeighbors(service, candidates)
                N = len(neighbors)
                index = (N - 1) // itera
                # mutation
                s.mutate(service, neighbors[index])

                Q = f(s,minQos , maxQos)
                if Q > fitnessList[i]:
                    fitnessList[i] = Q
                    limit[i] = 0
                else:
                    s.mutate(neighbors[index], service)  # mutation reset
                    limit[i] += 1
        # scout bees phase
        for i in range(SN):
            if limit[i] == SQ:  # scouts bee condition verified
                minIndex = solutions.index(min(solutions, key=lambda x: f(x,minQos , maxQos)))  # lowest fitness
                if itera >= CP:
                    # Best two solutions so far
                    best1 = solutions.index(max(solutions, key=lambda x: f(x,minQos , maxQos)))
                    aux = copy.deepcopy(solutions)
                    aux.remove(aux[best1])
                    best2 = aux.index(max(aux, key=lambda x: f(x,minQos , maxQos)))
                    # Crossover
                    child = cloud.crossover(solutions[best1], solutions[best2])
                    solutions[minIndex] = child
                else:
                    # Scouting
                    w = cloud.randomCompositionPlan(rootAct, actGraph, candidates)
                    solutions[minIndex] = w
                    #updateListQos(w , listQos , minQos , maxQos)
                    fitnessList[minIndex] = f(solutions[minIndex],minQos , maxQos)

                limit[minIndex] = 0

    sol = max(solutions, key=lambda x: f(x, minQos , maxQos))
    return(sol.globalQos(minQos,maxQos))
