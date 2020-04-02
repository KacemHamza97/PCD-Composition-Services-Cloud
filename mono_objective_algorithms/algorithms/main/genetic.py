from math import inf
from random import sample, uniform , random
from numpy.random import choice
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import crossover, mutate
from mono_objective_algorithms.algorithms.operations.fitness import fit 
from mono_objective_algorithms.algorithms.operations.update import updateBest , updateMinMax


#+----------------------------------------------------------------------------------------------+#


# G : n of generations  , N : size of population
# CP : crossover probability , CM : mutation probability

def genetic(problem, N, G, CP, CM):

    # population initializing
    population = list()
    
    minQos = {'responseTime': inf, 'price': inf, 'availability': inf, 'reliability': inf}
    maxQos = {'responseTime': 0, 'price': 0, 'availability': 0, 'reliability': 0}

    for i in range(N):
        while 1:
            cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())
            if cp.verifyConstraints(problem.getConstraints()):
                population.append(Solution(cp = cp , fitness = 0 , probability = 0))
                break

    # minQos maxQos and fitness initializing
    updateMinMax(population , minQos, maxQos , problem.getWeights())


    #+----------------------------------------------------------------------------------------------+#


    # Algorithm
    for generation in range(G):

        print(f"Completed = {((generation+1)/G)*100:.2f}%" , end = '\r')
        # Probability update
        s = sum([indiv.fitness for indiv in population])
        for indiv in population:
            indiv.probability = indiv.fitness / s

        # onlooker bees phase
        probabilityList = [indiv.probability for indiv in population]
        a = min(probabilityList)
        b = max(probabilityList)
        parents = []
        offsprings = []
        # Selecting best individuals
        for indiv in population:
            if indiv.probability > uniform(a,b):
                parents.append(indiv)
        
        # Mating selection
        for itera in range(len(parents)) :
            parent1 , parent2 =  sample(parents , 2)

            while 1:
                offspring = crossover(parent1.cp, parent2.cp, CP)  # Recombining
                if random() < CM : # Mutation
                    service = offspring.randomService()
                    random_service = choice(problem.getCandidates()[service.getActivity()])
                    offspring = mutate(offspring, random_service)
                if offspring.verifyConstraints(problem.getConstraints()):
                    offspring = Solution(cp = offspring , fitness = 0 , probability = 0)
                    offspring.fitness = fit(offspring, minQos, maxQos, problem.getWeights())
                    offsprings.append(offspring)
                    break
        
        # Adding offsprings
        population.extend(offsprings)

        # Keeping best individuals
        population = sorted(population, key = lambda indiv : indiv.fitness , reverse=True)[:N]

        updateMinMax(population , minQos, maxQos , problem.getWeights())
    
    # end of algorithm
    print("")
    return population[0].cp , minQos , maxQos
