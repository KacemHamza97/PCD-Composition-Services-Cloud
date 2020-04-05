from random import sample

from numpy import array

from data_structure.CompositionPlan import CompositionPlan
from data_structure.Problem import Problem
from data_structure.Solution import Solution
from genetic_operations.implementation import BSG
from multi_objective_algorithms.algorithms.operations.objective_functions import dominates


def functions(cp):
    QosDict = cp.cpQos()
    f1 = - QosDict["responseTime"]
    f2 = - QosDict["price"]
    f3 = QosDict["availability"] + QosDict["reliability"]
    return array([f1, f2, f3])  # Objective functions


def distance(sol1, sol2):
    QosDict1 = sol1.cp.cpQos()
    QosDict2 = sol2.cp.cpQos()

    f1 = QosDict1["responseTime"] - QosDict2["responseTime"]
    f2 = QosDict1["price"] - QosDict2["price"]
    f3 = (QosDict1["availability"] + QosDict1["reliability"]) - (QosDict2["availability"] + QosDict2["reliability"])
    return (f1 ** 2 + f2 ** 2 + f3 ** 2) ** 0.5  # euclidien distance


def SPEA2(problem):
    ############################# operations definition ##################################

    def intialize(n):
        L = []
        for i in range(n):
            while 1:
                cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())
                if cp.verifyConstraints(problem.getConstraints()):
                    L.append(Solution(cp=cp, fitness=0, functions=functions(cp)))
                    break
        return L

    def strength(solution):
        s = 1
        for sol in (P + EA):
            if dominates(sol, solution):
                s += 1
        return s  # strength of a solution

    # rawfitness is to minimize !
    def rawFitness(solution):
        return sum([strength(sol) for sol in (P + EA) if dominates(sol, solution)])

    def fit(solution, P, EA, k):
        dist = []
        L = P + EA
        for wiou in L:
            dist.append(distance(solution, wiou))
        dist.sort()
        value = dist[k]
        return 1 / (value + 2) + rawFitness(solution)  # fitness of a comosition plan

    def nondominated_individuals(P, EA):
        non_dominated = []
        for sol1 in (P + EA):
            for sol2 in (P + EA):
                if dominates(sol2, sol1):
                    break
            non_dominated.append(sol1)
        return non_dominated

    def dominated_individuals(P):
        dominated_individuals = []
        for sol1 in P:
            for sol2 in P:
                if dominates(sol2, sol1):
                    dominated_individuals.append(sol1)
                    break
        return dominated_individuals

    def sort_population_by_fitness(X):
        return sorted(X, key=lambda x: x.fitness)

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

    def update_EA(dominated_individuals, EA):
        if len(EA) < EN:
            EA.extends(sort_population_by_fitness(dominated_individuals)[EN - len(EA)])
        elif len(EA) > EN:
            # EA = truncation(len(EA) - EN, EA)
            EA = EA[:EN]
        return EA

    def update_P(dominated_individuals, P):
        if len(P) < N:
            P.extends(sort_population_by_fitness(dominated_individuals)[N - len(P)])
        elif len(P) > N:
            # P = truncation(len(P) - N, P)
            P = P[:N]
        return P

    def binaryTournement(EA):
        p1, p2 = sample(EA, 2)
        p1 = p1 if dominates(p1, p2) else p2
        p3, p4 = sample(EA, 2)
        p3 = p3 if dominates(p3, p4) else p4
        return p1, p3

    ############################# Algorithm start  ##################################

    # initializing parameters

    N = 8  # N : Pooulation size
    EN = 5  # EN : archive size
    T = 5  # maximum number of generations
    k = int((EN + N) ** 0.5)  # k-th nearest data point number
    P = list()  # liste des solutions

    # initializing Population and archive
    P = intialize(N)
    EA = []  # archive
    # Algorithm
    for t in range(T):
        print(" len( EA ) = before", len(EA))
        for sol in P:
            sol.fitness = fit(sol, P, EA, k)
        for sol in EA:
            sol.fitness = fit(sol, P, EA, k)

        EA.extend(nondominated_individuals(P, EA))
        EA = update_EA(dominated_individuals, EA)
        P = update_P(dominated_individuals, P)
        print("la taille de EA = after ", len(EA))
        parent1, parent2 = binaryTournement(EA)
        offspring_list = BSG(parent1.cp, parent2.cp, problem.getConstraints(), problem.getCandidates())
        for offspring in offspring_list:
            P.append(Solution(cp=offspring, fitness=0, functions=functions(offspring)))
        print(" len( P ) = ", len(P))

    return EA


n_act = int(input("NUMBER OF ACTIVITIES : "))
n_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': n_act * 0.3, 'price': n_act * 1.55, 'availability': 0.945 ** n_act, 'reliability': 0.825 ** n_act}

# problem init

p = Problem(n_act, n_candidates, constraints)
result = SPEA2(p)
for i in result:
    print(i)
