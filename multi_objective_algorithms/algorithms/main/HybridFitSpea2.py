from random import uniform, sample
from numpy.random import choice
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import mutate, generateOffsprings, crossover
from multi_objective_algorithms.algorithms.operations.objective_functions import functions
from multi_objective_algorithms.algorithms.operations.objective_functions import dominates
from multi_objective_algorithms.algorithms.operations.update import nonDominatedSort, transform, \
    normalize, normalized_Euclidean_Distance, updateSolutionsFitSPEA2

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
        dist.append(normalized_Euclidean_Distance(indiv1, indiv2, norm))
    dist.sort()
    value = dist[k]
    return 1 / (value + 2) + rawFitness(indiv1, U)
# +----------------------------------------------------------------------------------------------+#
def nondominated_individuals(U):
    non_dominated = []
    for indiv1 in (U):
        dominated = False
        for indiv2 in (U):
            if dominates(indiv2, indiv1):
                dominated = True
                break
        if not dominated :
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
                distances.append((sol1, sol2, normalized_Euclidean_Distance(sol1, sol2, norm)))

                # sorting distances
    distances.sort(key=lambda dist: dist[2])
    to_remove = list()  # list of solutions to remove
    for dist in distances:
        if len(to_remove) < n and to_remove.count(dist[1])==0:
            to_remove.append(dist[1])

    return [sol for sol in X if sol not in to_remove]


# +----------------------------------------------------------------------------------------------+#

def update(dominated_individuals, X, N):
    if len(X) < N:
        K = sort_population_by_fitness(dominated_individuals)
        X.extend(K[:N - len(X)])
    elif len(X) > N :
        X = truncation(len(X) - N, X)
    return X


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


# SQ : condition for scouts , MCN : number of iterations , SN : number of ressources , N : n of bees

def moabc_nsga2_spea2(problem, SQ, MCN, SN, N):

    k = int((SN + N) ** 0.5)  # k-th nearest data point number
    # solutions  initializing
    solutionsList = list()

    for i in range(SN):
        #while 1:
        cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())
        # if cp.verifyConstraints(problem.getConstraints()):
        solutionsList.append(Solution(cp=cp, fitness=0, functions=functions(cp)))
        # break
    Archive=[]
    # Algorithm
    for itera in range(MCN+1):

        U = set(solutionsList + Archive)
        # employed bees phase
        for indiv in U:
            indiv.fitness = fit(indiv, U, k)
        Archive = nondominated_individuals(U)

        if itera == MCN + 1:
            break

        Archive = update(dominated_individuals(solutionsList), Archive, N)

        exploited = []
        for itera in range(N // 4):
            exploited.extend(binaryTournement(Archive))
        solutionsList=[]
        #exploited= sample(Archive,len(Archive)//4)
        for itera in range(N // 4):
            while 1:
                parent1, parent2 = sample(exploited, 2)
                if parent1.cp != parent2.cp:
                    break

            # Applying crossover and mutation
            offsprings=[]
            res=crossover(parent1.cp, parent2.cp, 0.5)
            offsprings.append(res)
            service = res.randomService()
            while 1:
                neighbor = choice(problem.getCandidates()[service.getActivity()])
                if neighbor != service:
                    break
            offsprings.append(mutate(res, neighbor))
            # Adding offsprings
            solutionsList += [Solution(cp=cp, fitness=0, functions=functions(cp)) for cp in offsprings]
            # end of employed bees phase

        for indiv in solutionsList:
            indiv.fitness = fit(indiv, solutionsList, k)

        solutionsList=sorted(solutionsList, key=lambda indiv: indiv.fitness, reverse=True)
        exploited=solutionsList[0:len(solutionsList)//2]
        #exploited=solutionsList[::2]

        # onlooker bees phase
        for sol in exploited:
                service = sol.cp.randomService()
                while 1:
                    neighbor = choice(problem.getCandidates()[service.getActivity()])
                    if neighbor != service:
                        break
                # mutation operation
                new = mutate(sol.cp, neighbor)
                # Adding offsprings
                solutionsList.append(Solution(cp=new, fitness=0, functions=functions(cp)))

        # end of onlooker bees phase

        # scout bees phase
        for itera in range(N//4):
            #while 1:
            cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())  # randomly generated cp
                    #if cp.verifyConstraints(problem.getConstraints()):
            solutionsList.append(Solution(cp=cp, fitness=0, functions=functions(cp)))
                        #break
                #nUpdate = 1
        # end of scout bees phase

    # end of algorithm
    return Archive
