import cloud
import copy


# services is a list made of list of services that perform a common activity , each list of services represents an activity
# services is indexed based on the attribut activity of each service (cloud.py)
# actGraph is a graph with only activities indexes linked to each other by arcs
# rootAct is the first activity

# sort neighbors of service based on euclidean distance from the nearest to the furthest

def getNeighbors(s, candidateServices):  # s is a service
    candidates = candidateServices[s.getActivity() - 1]
    return sorted([neighbor for neighbor in candidates if neighbor != s], key=lambda x: s.euclideanDist(x))


# Objective function
def f(compositionplan):
    res = compositionplan.QoS() + compositionplan.evaluateMatching()
    return res + 1


# return workflow.evaluateMatching()

# SC : condition for scouts , MCN : termination condition , SN : number of workflows , p :probability
def ABCgenetic(rootAct, actGraph, services, SQ, MCN, SN, p):
    # initializing

    solutions = list()
    fitnessList = list()
    probabilityList = list(0 for i in range(SN))
    limit = list(0 for i in range(SN))
    CP = 4 * MCN / 5  # changing point for scouts

    # solutions and fitness initializing

    for i in range(SN):
        solutions.append(cloud.randomCompositionPlan(rootAct, actGraph, services))
    for i in range(SN):
        fitnessList.append(f(solutions[i]))

    # Algorithm
    for itera in range(1, MCN + 1):

        # working bees phase
        for i in range(SN):
            s = solutions[i]  # s is a workflow
            # choose randomly a service to mutate
            service = s.randomServ()
            # new service index
            neighbors = getNeighbors(service, services)
            N = len(neighbors)
            index = (N - 1) // itera
            # mutation
            s.mutate(service, neighbors[index])
            cloud.CompositionPlan.qos_Composition_Plan.extend([[s.evaluateResponseTime(), s.evaluatePrice(), s.evaluateAvailability(), s.evaluateReliability()]])
            Q = f(s)
            if Q > fitnessList[i]:
                fitnessList[i] = Q
                limit[i] = 0
            else:
                cloud.CompositionPlan.qos_Composition_Plan.pop(cloud.CompositionPlan.qos_Composition_Plan.index([s.evaluateResponseTime(), s.evaluatePrice(), s.evaluateAvailability(),s.evaluateReliability()]))
                s.mutate(neighbors[index], service)  # mutation reset
                cloud.CompositionPlan.qos_Composition_Plan.extend([[s.evaluateResponseTime(), s.evaluatePrice(), s.evaluateAvailability(), s.evaluateReliability()]])

                limit[i] += 1

        # Probability update
        for i in range(SN):
            s = solutions[i]
            probabilityList[i] = f(s) / sum(fitnessList)

        # onlooker bees phase
        for i in range(SN):
            if probabilityList[i] > p:
                s = solutions[i]  # s is a workflow
                # choose randomly a service to mutate
                service = s.randomServ()
                # new service index
                neighbors = getNeighbors(service, services)
                N = len(neighbors)
                index = (N - 1) // itera
                # mutation
                s.mutate(service, neighbors[index])
                cloud.CompositionPlan.qos_Composition_Plan.extend([[s.evaluateResponseTime(), s.evaluatePrice(), s.evaluateAvailability(), s.evaluateReliability()]])
                Q = f(s)
                if Q > fitnessList[i]:
                    fitnessList[i] = Q
                    limit[i] = 0
                else:
                    cloud.CompositionPlan.qos_Composition_Plan.pop(cloud.CompositionPlan.qos_Composition_Plan.index([s.evaluateResponseTime(), s.evaluatePrice(), s.evaluateAvailability(),s.evaluateReliability()]))
                    s.mutate(neighbors[index], service)  # mutation reset
                    cloud.CompositionPlan.qos_Composition_Plan.extend([[s.evaluateResponseTime(), s.evaluatePrice(), s.evaluateAvailability(),s.evaluateReliability()]])
                    limit[i] += 1
        # scout bees phase
        for i in range(SN):
            if limit[i] == SQ:  # scouts bee condition verified
                minIndex = solutions.index(min(solutions, key=lambda x: f(x)))  # lowest fitness
                if itera >= CP:
                    # Best two solutions so far
                    best1 = solutions.index(max(solutions, key=lambda x: f(x)))
                    aux = copy.deepcopy(solutions)
                    aux.remove(aux[best1])
                    best2 = aux.index(max(aux, key=lambda x: f(x)))
                    # Crossover
                    child = cloud.crossover(solutions[best1], solutions[best2])
                    solutions[minIndex] = child
                    cloud.CompositionPlan.qos_Composition_Plan.extend([[child.evaluateResponseTime(), child.evaluatePrice(), child.evaluateAvailability(),child.evaluateReliability()]])
                else:
                    # Scouting
                    solutions[minIndex] = cloud.randomCompositionPlan(rootAct, actGraph, services)
                    fitnessList[minIndex] = f(solutions[minIndex])

                limit[minIndex] = 0

    return max(solutions, key=lambda x: f(x))
