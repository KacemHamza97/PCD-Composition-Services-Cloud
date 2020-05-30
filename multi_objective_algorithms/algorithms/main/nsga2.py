from random import uniform, sample , random
from numpy.random import choice
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import BSG
from multi_objective_algorithms.algorithms.operations.objective_functions import functions , fit
from multi_objective_algorithms.algorithms.operations.update import updateSolutions, nonDominatedSort


# +----------------------------------------------------------------------------------------------+#


# G : n of generations  , N : size of population
# CP : crossover probability , CM : mutation probability

def nsga2(problem, G, N):
    # population  initializing
    population = list()

    for i in range(N):
        while 1:
            cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())
            if cp.verifyConstraints(problem.getConstraints()):
                population.append(Solution(cp=cp, fitness=0, functions=functions(cp), probability=0))
                break

    # fitness initializing

    for indiv in population:
        indiv.fitness = fit(indiv, population)

    # Algorithm
    for itera in range(G):

        # Probability update
        s = sum([indiv.fitness for indiv in population])
        for indiv in population:
            indiv.probability = indiv.fitness / s

        probabilityList = [indiv.probability for indiv in population]
        a = min(probabilityList)
        b = max(probabilityList)

        U = list()
        U[:] = population
        parents = []
        offsprings = []
        # Selecting best individuals
        n_individuals = 0
        while n_individuals < 2:
            for indiv in population:
                if indiv.probability >= uniform(a, b):
                    n_individuals += 1
                    parents.append(indiv)

        # Mating selection
        for itera in range(len(parents) // 2):
            parent1, parent2 = sample(parents, 2)

            # Applying BSG
            cp1 = parent1.cp
            cp2 = parent2.cp
            offsprings = BSG(cp1, cp2, problem.getConstraints(), problem.getCandidates())  # BSG

            # Adding offsprings
            U += [Solution(cp=cp, fitness=0, functions=functions(cp), probability=0) for cp in offsprings]

        # Finalizing generation
        fronts = nonDominatedSort(U)
        population = updateSolutions(population, fronts, "crowdingSort")

    # end of algorithm
    return fronts[0]
