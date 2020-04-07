from random import sample
from numpy import array
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import BSG
from multi_objective_algorithms.algorithms.operations.objective_functions import functions
from multi_objective_algorithms.algorithms.operations.objective_functions import dominates

#+----------------------------------------------------------------------------------------------+#

def distance(indiv1, indiv2):
    QosDict1 = indiv1.cp.cpQos()
    QosDict2 = indiv2.cp.cpQos()

    f1 = QosDict1["responseTime"] - QosDict2["responseTime"]
    f2 = QosDict1["price"] - QosDict2["price"]
    f3 = (QosDict1["availability"] + QosDict1["reliability"]) - (QosDict2["availability"] + QosDict2["reliability"])
    return (f1 ** 2 + f2 ** 2 + f3 ** 2) ** 0.5  # euclidien distance

#+----------------------------------------------------------------------------------------------+#

def strength(indiv1 , population , EA):
        s = 1
        for indiv2 in (population + EA):
            if dominates(indiv1, indiv2):
                s += 1


#+----------------------------------------------------------------------------------------------+#

# rawfitness is to minimize !

def rawFitness(indiv1, population , EA):
    return sum([strength(indiv2, population , EA) for indiv2 in (population + EA) if dominates(indiv2, indiv1)])


#+----------------------------------------------------------------------------------------------+#

def fit(indiv1, population, EA, k):
    dist = []
    for indiv2 in population + EA:
        dist.append(distance(indiv1, indiv2))
    dist.sort()
    value = dist[k]
    return 1 / (value + 2) + rawFitness(indiv1, population , EA)  

#+----------------------------------------------------------------------------------------------+#

def nondominated_individuals(population, EA):
        non_dominated = []
        for indiv1 in (population + EA):
            for indiv2 in (population + EA):
                if dominates(indiv2, indiv1):
                    break
            non_dominated.append(indiv1)
        return non_dominated

#+----------------------------------------------------------------------------------------------+#

def dominated_individuals(population):
        dominated_individuals = []
        for indiv1 in population:
            for indiv2 in population:
                if dominates(indiv2, indiv1):
                    dominated_individuals.append(indiv1)
                    break
        return dominated_individuals

#+----------------------------------------------------------------------------------------------+#

def sort_population_by_fitness(population):
        return sorted(population, key=lambda indiv: indiv.fitness)

#+----------------------------------------------------------------------------------------------+#

def truncation(n, EA):
        d = []
        e = set()
        for i, d1 in enumerate(EA):
            e.add(i)
            for j, d2 in enumerate(EA):
                if j not in e:  # astuce pour ne pas calculer la distance (d1 , d2) et (d2,d1)
                    d.append((d1, d2, distance(d1, d2)))  # tuple (d1,d2,distance)
        d.sort(key=lambda x: x[2])  # sort by distance
        L = []
        for elem in d:
            if len(L) < n and elem[0] not in L and elem[1] not in L:
                # the 3rd condition : to avoid deleting some thing had been deleted exemple fig 2 page 9
                L.append(elem[1])
        for elem in EA:
            if elem in L:
                EA.remove(elem)
        return EA

#+----------------------------------------------------------------------------------------------+#

def update_EA(dominated_individuals, EA , EN):
        if len(EA) < EN:
            EA.extends(sort_population_by_fitness(dominated_individuals)[EN - len(EA)])
        elif len(EA) > EN:
            EA = truncation(len(EA) - EN, EA)
            EA = EA[:EN]
        return EA

#+----------------------------------------------------------------------------------------------+#

def updatePopulation(dominated_individuals, population , N):
        if len(population) < N:
            population.extends(sort_population_by_fitness(dominated_individuals)[N - len(population)])
        elif len(population) > N:
            # population = truncation(len(population) - N, population)
            population = population[:N]
        return population

#+----------------------------------------------------------------------------------------------+#

def binaryTournement(EA):
        p1, p2 = sample(EA, 2)
        p1 = p1 if dominates(p1, p2) else p2
        p3, p4 = sample(EA, 2)
        p3 = p3 if dominates(p3, p4) else p4
        return p1, p3

#+----------------------------------------------------------------------------------------------+#

# N : Population size , EN : archive size , G : number of generations

def spea2(problem , G , N , EN):


    # initializing parameters

    k = int((EN + N) ** 0.5)  # k-th nearest data point number

    # population  initializing

    population = list()

    for i in range(N):
        while 1:
            cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())
            if cp.verifyConstraints(problem.getConstraints()):
                population.append(Solution(cp=cp, fitness=0, functions=functions(cp)))
                break

    # Initializing archive
    EA = [] 

    # Algorithm
    for generation in range(G):
        for indiv in population:
            indiv.fitness = fit(indiv, population, EA, k)
        for indiv in EA:
            indiv.fitness = fit(indiv, population, EA, k)

        EA.extend(nondominated_individuals(population, EA))
        EA = update_EA(dominated_individuals, EA , EN)
        population = updatePopulation(dominated_individuals, population , N)
        parent1, parent2 = binaryTournement(EA)
        offspring_list = BSG(parent1.cp, parent2.cp, problem.getConstraints(), problem.getCandidates())
        for offspring in offspring_list:
            population.append(Solution(cp=offspring, fitness=0, functions=functions(offspring)))

    return EA
