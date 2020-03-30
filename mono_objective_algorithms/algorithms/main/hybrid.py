from math import inf
from random import sample, uniform, randint
from mono_objective_algorithms.algorithms.genetic_operation.genetic_operations import crossover, mutate
from mono_objective_algorithms.algorithms.objective_function.Qos_constraints import verifyConstraints
from mono_objective_algorithms.algorithms.objective_function.fitness import fit
from data_structure.Composition_plan import CompositionPlan


def getNeighbor(service, candidates):
    return min([neighbor for neighbor in candidates if neighbor != service], key=lambda x: service.euclideanDist(x))


# SQ : condition for scouts , MCN : number of iterations
def ABCgenetic(actGraph, candidates, SN, SQ, MCN, SCP, N,CP, constraints, weights):
    def updateBest(fit=None):
        nonlocal best_fit, best_cp
        if fit == None:  # No parameters passed
            fit = max(fitnessList)

        if fit > best_fit:
            best_fit = fit  # Updating best fitness
            best_cp = solutionsList[fitnessList.index(fit)]  # Updating best solution

    def updateMinMax():
        nonlocal best_fit, fitnessList, minQos, maxQos
        # updating minQos and maxQos
        # looking for minQos and maxQos in best_Qos
        try:
            best_cp_Qos = best_cp.cpQos()
            for qos in best_cp_Qos:
                if best_cp_Qos[qos] < minQos[qos]:
                    minQos[qos] = best_cp_Qos[qos]
                if best_cp_Qos[qos] > maxQos[qos]:
                    maxQos[qos] = best_cp_Qos[qos]
        except:  # best_Qos not created
            print("")
        # looking for minQos and maxQos in solutionsList
        for cp in solutionsList:
            qosDict = cp.cpQos()
            for qos in qosDict:
                if qosDict[qos] < minQos[qos]:
                    minQos[qos] = qosDict[qos]
                if qosDict[qos] > maxQos[qos]:
                    maxQos[qos] = qosDict[qos]
        # Updating best fitness
        try:
            best_fit = fit(best_cp, minQos, maxQos, weights)
        except:  # best_cp not created
            None
        # updating fitnessList
        for i in range(SN):
            fitnessList[i] = fit(solutionsList[i], minQos, maxQos, weights)

    ############################# Algorithm start  ##################################

    # solutions and fitness initializing
    solutionsList = list()
    fitnessList = list(0 for i in range(SN))
    probabilityList = list(0 for i in range(SN))
    minQos = {'responseTime': inf, 'price': inf, 'availability': inf, 'reliability': inf}
    maxQos = {'responseTime': 0, 'price': 0, 'availability': 0, 'reliability': 0}
    limit = list(0 for i in range(SN))

    for i in range(SN):
        while 1:
            cp = CompositionPlan(actGraph, candidates)
            if verifyConstraints(cp.cpQos(), constraints):
                solutionsList.append(cp)
                break

    # minQos maxQos and fitnessList initializing
    updateMinMax()

    # initializing best_fit and best_cp
    best_fit = max(fitnessList)
    best_cp = solutionsList[fitnessList.index(best_fit)]
    # Algorithm
    for itera in range(MCN):
        # employed bees phase
        exploited = sample(list(range(SN)), N)  # Generating positions list for exploitation
        for i in exploited:
            cp1 = solutionsList[i]
            while 1:
                cp2 = CompositionPlan(actGraph, candidates)  # randomly generated cp
                child = crossover(cp1, cp2, CP)  # Crossover operation
                if verifyConstraints(child.cpQos(), constraints):
                    new_fitness = fit(child, minQos, maxQos, weights)
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
        for i in exploited:
            probabilityList[i] = fitnessList[i] / s

        # onlooker bees phase
        for i in exploited:
            if probabilityList[i] > uniform(min(probabilityList), max(probabilityList)):
                cp1 = solutionsList[i]
                cp2 = best_cp  # current best
                while 1:
                    child = crossover(cp1, cp2, CP)  # Crossover operation
                    if verifyConstraints(child.cpQos(), constraints):
                        new_fitness = fit(child, minQos, maxQos, weights)
                        if new_fitness > fitnessList[i]:  # checking if child fitness is better than parent fitness
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
                if itera >= SCP:  # change of scouts behaviour condition to mutating
                    cp = solutionsList[i]
                    while 1:
                        # choose randomly a service to mutate
                        service = cp.G.nodes[randint(0, cp.G.number_of_nodes() - 1)]["service"]
                        neighborsList = candidates[service.getActivity()]
                        neighbor = getNeighbor(service, neighborsList)
                        # mutation operation
                        new = mutate(cp, neighbor)
                        if verifyConstraints(new.cpQos(), constraints):
                            solutionsList[i] = new
                            fitnessList[i] = fit(new, minQos, maxQos, weights)
                            break

                else:  # searching for new ressources to exploit
                    while 1:
                        cp = CompositionPlan(actGraph, candidates)
                        if verifyConstraints(cp.cpQos(), constraints):
                            solutionsList[i] = cp
                            fitnessList[i] = fit(cp, minQos, maxQos, weights)
                            break
                limit[i] = 0
        # end of scout bees phase
        updateMinMax()

    # end of algorithm
    return best_cp , minQos , maxQos
