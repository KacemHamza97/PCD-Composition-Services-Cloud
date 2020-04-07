from numpy import array
from random import sample
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import BSG
from multi_objective_algorithms.algorithms.operations.objective_functions import functions
from multi_objective_algorithms.algorithms.operations.objective_functions import dominates
from data_structure.Problem import Problem

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
        return s


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

# n : number of elements to remove from X
def truncation(n, X):
        # evaluating distances 
        distances = []      # list of tuples (sol1 , sol2 , distance)
        e = set()           
        for i, sol1 in enumerate(X):
            e.add(i)        # avoid calculating same distance twice
            for j, sol2 in enumerate(X):
                if j not in e:  
                    distances.append((sol1, sol2, distance(sol1, sol2)))  

        # sorting distances
        distances.sort(key=lambda dist: dist[2])  
        remove = list()  # list of solutions to remove 
        for dist in distances:
            if len(remove) < n and dist[1] not in remove :
                remove.append(dist[1])
        for sol in X:
            if sol in remove:
                X.remove(sol)
        return X

#+----------------------------------------------------------------------------------------------+#

def update(dominated_individuals, X , N):
        if len(X) < N:
            X.extends(sort_population_by_fitness(dominated_individuals)[N - len(X)])
        elif len(X) > N:
            X = truncation(len(X) - N, X)
            X = X[:N]
        return X

#+----------------------------------------------------------------------------------------------+#

def notIN(sol1 , X) : 
    for sol2 in X : 
        if sol1.cp == sol2.cp :
            return False
    return True

#+----------------------------------------------------------------------------------------------+#

def binaryTournement(EA):
    final = []
    p1 , p2 = sample(EA , 2)
    final.append(p1) if dominates(p1, p2) else final.append(p2)
    while 1 : 
        p1 , p2 = sample(EA , 2)
        if notIN(p1,final) and notIN(p2 , final) :
            break
    final.append(p1) if dominates(p1, p2) else final.append(p2)

    print(final[0].cp == final[1].cp)
    return final[0] , final[1]


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
        print(f"completed = {(generation + 1) * 100 / G} %", end='\r')
        for indiv in population:
            indiv.fitness = fit(indiv, population, EA, k)
        for indiv in EA:
            indiv.fitness = fit(indiv, population, EA, k)

        EA.extend(nondominated_individuals(population, EA))
        EA = update(dominated_individuals, EA , EN)
        population = update(dominated_individuals, population , N)
        parent1 , parent2 = binaryTournement(EA)
        offspring_list = BSG(parent1.cp, parent2.cp, problem.getConstraints(), problem.getCandidates())
        for offspring in offspring_list:
            population.append(Solution(cp=offspring, fitness=0, functions=functions(offspring)))

    return EA
 