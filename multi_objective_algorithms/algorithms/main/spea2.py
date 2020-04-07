from random import sample
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import BSG
from multi_objective_algorithms.algorithms.operations.objective_functions import functions
from multi_objective_algorithms.algorithms.operations.objective_functions import dominates


# +----------------------------------------------------------------------------------------------+#

def distance(indiv1, indiv2):
    QosDict1 = indiv1.cp.cpQos()
    QosDict2 = indiv2.cp.cpQos()

    f1 = QosDict1["responseTime"] - QosDict2["responseTime"]
    f2 = QosDict1["price"] - QosDict2["price"]
    f3 = (QosDict1["availability"] + QosDict1["reliability"]) - (QosDict2["availability"] + QosDict2["reliability"])
    return (f1 ** 2 + f2 ** 2 + f3 ** 2) ** 0.5  # euclidien distance


# +----------------------------------------------------------------------------------------------+#

def strength(indiv1, U):
    s = 1
    for indiv2 in (U):
        if dominates(indiv1, indiv2):
            s += 1
    return s


# +----------------------------------------------------------------------------------------------+#

# rawfitness is to minimize !

def rawFitness(indiv1, U):
    return sum([strength(indiv2, U) for indiv2 in U if dominates(indiv2, indiv1)])


# +----------------------------------------------------------------------------------------------+#

def fit(indiv1, U, k):
    dist = []
    for indiv2 in U:
        dist.append(distance(indiv1, indiv2))
    dist.sort()
    value = dist[k]
    return 1 / (value + 2) + rawFitness(indiv1, U)


# +----------------------------------------------------------------------------------------------+#

def nondominated_individuals(U):
    non_dominated = []
    for indiv1 in (U):
        for indiv2 in (U):
            if dominates(indiv2, indiv1):
                break
        non_dominated.append(indiv1)
    return non_dominated


# +----------------------------------------------------------------------------------------------+#

def dominated_individuals(population):
    dominated_individuals = []
    for indiv1 in population:
        for indiv2 in population:
            if dominates(indiv2, indiv1):
                dominated_individuals.append(indiv1)
                break
    return dominated_individuals


# +----------------------------------------------------------------------------------------------+#

def sort_population_by_fitness(population):
    return sorted(population, key=lambda indiv: indiv.fitness)


# +----------------------------------------------------------------------------------------------+#

# n : number of elements to remove from X
def truncation(n, X):
    # evaluating distances
    distances = []  # list of tuples (sol1 , sol2 , distance)
    e = set()
    for i, sol1 in enumerate(X):
        e.add(i)  # avoid calculating same distance twice
        for j, sol2 in enumerate(X):
            if j not in e:
                distances.append((sol1, sol2, distance(sol1, sol2)))

                # sorting distances
    distances.sort(key=lambda dist: dist[2])
    remove = list()  # list of solutions to remove
    for dist in distances:
        if len(remove) < n and dist[1] not in remove:
            remove.append(dist[1])
    for sol in X:
        if sol in remove:
            X.remove(sol)
    return X


# +----------------------------------------------------------------------------------------------+#

def update(dominated_individuals, X, N):
    if len(X) < N:
        X.extends(sort_population_by_fitness(dominated_individuals)[N - len(X)])
    elif len(X) > N:
        X = truncation(len(X) - N, X)
        X = X[:N]


# +----------------------------------------------------------------------------------------------+#

def notIN(sol1, X):
    for sol2 in X:
        if sol1.cp == sol2.cp:
            return False
    return True


# +----------------------------------------------------------------------------------------------+#

def binaryTournement(mating_pool):
    final = []
    p1, p2 = sample(mating_pool, 2)
    final.append(p1) if p1.fitness > p2.fitness else final.append(p2)
    while 1:
        p3, p4 = sample(mating_pool, 2)
        if p3.cp != final[0].cp and p4.cp != final[0].cp:
            break
    final.append(p3) if p3.fitness > p4.fitness else final.append(p4)
    return final[0], final[1]


# +----------------------------------------------------------------------------------------------+#

# N : Population size , EN : archive size , G : number of generations

def spea2(problem, G, N, EN):
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
        print(f"completed = {(generation + 1) * 100 / G} %", end='\r')

        U = set(population + EA)

        for indiv in U:
            indiv.fitness = fit(indiv, U, k)

        next_EA = nondominated_individuals(U)
        update(dominated_individuals(U), next_EA, EN)

        mating_pool = sample(next_EA, EN // 2)

        next_generation = []
        for itera in range(EN // 4):
            parent1, parent2 = binaryTournement(mating_pool)
            offspring_list = BSG(parent1.cp, parent2.cp, problem.getConstraints(), problem.getCandidates())
            for offspring in offspring_list:
                next_generation.append(Solution(cp=offspring, fitness=0, functions=functions(offspring)))

        population = next_generation
        EA = next_EA
    return EA