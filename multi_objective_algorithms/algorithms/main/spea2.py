from random import sample
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import BSG
from multi_objective_algorithms.algorithms.operations.objective_functions import functions 
from multi_objective_algorithms.algorithms.operations.objective_functions import dominates
from multi_objective_algorithms.algorithms.operations.update import normalize , normalized_Euclidean_Distance , transform


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
    norm = normalize(transform(U))
    for indiv2 in U:
        dist.append(normalized_Euclidean_Distance(indiv1, indiv2 , norm))
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
    norm = normalize(transform(X))
    for i, sol1 in enumerate(X):
        e.add(i)  # avoid calculating same distance twice
        for j, sol2 in enumerate(X):
            if j not in e:
                distances.append((sol1, sol2, normalized_Euclidean_Distance(sol1, sol2 ,norm)))

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
        X.extend(sort_population_by_fitness(dominated_individuals)[N - len(X)])
    elif len(X) > N:
        X = truncation(len(X) - N, X)[:N]


# +----------------------------------------------------------------------------------------------+#


def binaryTournement(X):
    final = []
    p1, p2 = sample(X, 2)
    final.append(p1) if p1.fitness > p2.fitness else final.append(p2)
    while 1:
        p3, p4 = sample(X, 2)
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
    for generation in range(G+1):

        U = set(population + EA)

        for indiv in U:
            indiv.fitness = fit(indiv, U, k)

        EA = nondominated_individuals(U)

        if generation == G+1 :
            break

        update(dominated_individuals(U), EA, EN)

        # Creating the mating_pool
        mating_pool = []
        for itera in range(EN // 4) :
            mating_pool.extend(binaryTournement(EA))

        next_generation = []
        # Creating new generation
        for itera in range(EN // 4) : 
            # Selecting parents for offsprings generation
            while 1:
                parent1, parent2 = sample(mating_pool, 2)
                if parent1.cp != parent2.cp :
                    break

    
            # Applying BSG
            offsprings = BSG(parent1.cp, parent2.cp, problem.getConstraints(), problem.getCandidates())
            # Adding offsprings
            next_generation += [Solution(cp = cp , fitness = 0 , functions = functions(cp)) for cp in offsprings]

        population = next_generation

    return EA