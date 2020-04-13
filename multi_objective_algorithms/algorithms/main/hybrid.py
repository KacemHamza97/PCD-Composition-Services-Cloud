from random import uniform, sample
from numpy.random import choice
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import BSG
from multi_objective_algorithms.algorithms.operations.objective_functions import functions
from multi_objective_algorithms.algorithms.operations.update import updateSolutions, nonDominatedSort


# +----------------------------------------------------------------------------------------------+#


# SQ : condition for scouts , MCN : number of iterations , SN : number of ressources , N : n of bees 

def moabc_nsga2(problem, SQ, MCN, SN, N):
    # solutions  initializing
    solutionsList = list()

    for i in range(SN):
        while 1:
            cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())
            if cp.verifyConstraints(problem.getConstraints()):
                solutionsList.append(Solution(cp=cp, functions=functions(cp), probability=0, limit=0))
                break

    # Algorithm
    for itera in range(MCN):

        # employed bees phase
        exploited = sample(solutionsList, N)  # selecting solutions for exploitation randomly
        U = list()
        U[:] = solutionsList
        for sol in exploited:
            cp1 = sol.cp
            cp2 = CompositionPlan(problem.getActGraph(), problem.getCandidates()) # randomly generated
            offsprings = BSG(cp1, cp2, problem.getConstraints(), problem.getCandidates())  # BSG
            # Adding offsprings
            U += [Solution(cp = cp , functions = functions(cp) ,limit = 0) for cp in offsprings]
        # end of employed bees phase

        fronts = nonDominatedSort(U)
        solutionsList = updateSolutions(solutionsList, fronts, method="crowdingSort")

        # onlooker bees phase
        U = list()
        U[:] = solutionsList
        pf = fronts[0]
        if len(pf) < 3 :
            pf += fronts[1]
        for itera in range(N):
            # cp 1 randomly chosen from pf
            cp1 = choice(pf).cp
            # cp 2 randomly chosen from pf
            while 1:
                cp2 = choice(pf).cp
                if cp2 != cp1:
                    break
                offsprings = BSG(cp1, cp2, problem.getConstraints(), problem.getCandidates())  # BSG
                # Adding offsprings
                U += [Solution(cp = cp , functions = functions(cp) ,limit = 0) for cp in offsprings]

        # end of onlooker bees phase

        fronts = nonDominatedSort(U)
        solutionsList = updateSolutions(solutionsList, fronts, "crowdingSort")
        

        # scout bees phase
        update = 0
        U = list()
        U[:] = solutionsList
        for sol in exploited:
            if sol.limit >= SQ and sol not in fronts[0] :
                sol.limit = 0
                while 1:
                    cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())  # randomly generated cp
                    if cp.verifyConstraints(problem.getConstraints()):
                        U.append(Solution(cp = cp ,functions = functions(cp) ,limit = 0))
                        break
                update = 1
        # end of scout bees phase
        if update:
            fronts = nonDominatedSort(U)
            solutionsList = updateSolutions(solutionsList, fronts, "crowdingSort")


    # end of algorithm
    return fronts[0]
