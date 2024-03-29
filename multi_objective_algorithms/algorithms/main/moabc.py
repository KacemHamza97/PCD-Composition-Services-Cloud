from random import uniform, sample
from numpy.random import choice
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import mutate
from multi_objective_algorithms.algorithms.operations.objective_functions import functions
from multi_objective_algorithms.algorithms.operations.update import updateSolutions, nonDominatedSort


# +----------------------------------------------------------------------------------------------+#


# SQ : condition for scouts , MCN : number of iterations , SN : number of ressources , N : n of bees 

def moabc(problem, SQ, MCN, SN):
    # solutions  initializing
    solutionsList = list()

    for i in range(SN):
        while 1:
            cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())
            if cp.verifyConstraints(problem.getConstraints()):
                solutionsList.append(Solution(cp=cp, fitness=0, functions=functions(cp), probability=0, limit=0))
                break

    # Algorithm
    for itera in range(MCN):

        # employed bees phase
        U = list()
        U[:] = solutionsList
        for sol in solutionsList:
            while 1:
                # choose randomly a service to mutate
                service = sol.cp.randomService()
                while 1:
                    neighbor = choice(problem.getCandidates()[service.getActivity()])
                    if neighbor != service:
                        break
                # mutation operation
                new = mutate(sol.cp, neighbor)
                if new.verifyConstraints(problem.getConstraints()):
                    U.append(Solution(cp=new, fitness=0, functions=functions(new), probability=0, limit=0))
                    break

        # end of employed bees phase

        fronts = nonDominatedSort(U)
        solutionsList = updateSolutions(solutionsList, fronts, method="crowdingSort")

        # Probability update
        s = sum([sol.fitness for sol in solutionsList])
        for sol in solutionsList:
            sol.probability = sol.fitness / s

        # onlooker bees phase
        probabilityList = [sol.probability for sol in solutionsList]
        a = min(probabilityList)
        b = max(probabilityList)
        U = list()
        U[:] = solutionsList
        for sol in solutionsList:
            if sol.probability > uniform(a, b):
                while 1:
                    # choose randomly a service to mutate
                    service = sol.cp.randomService()
                    while 1:
                        neighbor = choice(problem.getCandidates()[service.getActivity()])
                        if neighbor != service:
                            break
                    # mutation operation
                    new = mutate(sol.cp, neighbor)
                    if new.verifyConstraints(problem.getConstraints()):
                        U.append(Solution(cp=new, fitness=0, functions=functions(new), probability=0, limit=0))
                        break

        # end of onlooker bees phase

        fronts = nonDominatedSort(U)
        solutionsList = updateSolutions(solutionsList, fronts, "crowdingSort")

        # scout bees phase
        update = 0
        U = list()
        U[:] = solutionsList
        for sol in solutionsList:
            if sol.limit >= SQ and sol not in fronts[0]:
                while 1:
                    cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())  # randomly generated cp
                    if cp.verifyConstraints(problem.getConstraints()):
                        U.append(Solution(cp=cp, fitness=0, functions=functions(cp), probability=0, limit=0))
                        break
                update = 1

        # end of scout bees phase
        if update:
            fronts = nonDominatedSort(U)
            solutionsList = updateSolutions(solutionsList, fronts, "crowdingSort")
    # end of algorithm
    return fronts[0]
