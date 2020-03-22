import cloud , hybrid , moabc , time , csv , nsga2
import numpy as np
from math import inf
from pymoo.factory import get_performance_indicator

def generateActGraph(actNum):       # Sequential
    return [[i, i + 1, 0] for i in range(actNum - 1)]


def generateCandidates(actNum, num_candidates):
    candidates = list()
    for i in range(actNum) :
        candidates.append([])
        for j in range(num_candidates):
            responseTime = np.random.uniform(0.1, 5, 1)[0]
            price = np.random.uniform(0.1, 3, 1)[0]
            availability = np.random.uniform(0.9, 0.99, 1)[0]
            reliability = np.random.uniform(0.7, 0.95, 1)[0]
            candidates[i].append(cloud.Service(i, responseTime, reliability, availability, price, matching=1))
    return candidates

def nonDominatedSort(X) :
    pareto = []
    SList = list()
    NList = list()
    for p in range(len(X)) :
        Sp = list()
        Np = 0
        F = X[p]["functions"]
        for q in range(len(X)) :
            G = X[q]["functions"]
            if q != p and (F >= G).all() and (F > G).any() :
                Sp.append(q)
            elif q != p and (G >= F).all() and (G > F).any() :
                Np += 1
        if Np == 0 :
            pareto.append(p)

    return [X[p] for p in pareto]


def crowdingSort(front) :
    scoresList = list()
    for p in front :
        score = list()
        for f in range(3) :
            high = []
            low = []
            for q in front :
                if q["functions"][f] < p["functions"][f]  :
                    low.append(q["functions"][f])
                if q["functions"][f] > p["functions"][f] :
                    high.append(q["functions"][f])
            if len(high) == 0 :
                next_high = p["functions"][f]
            else :
                next_high = min(high)
            if len(low) == 0 :
                 next_low = p["functions"][f]
            else :
                next_low = max(low)
            score.append(next_high-next_low)
        scoresList.append(sum(score))

    return [i[1] for i in sorted(zip(scoresList , front) , key = lambda x:x[0] , reverse = True)]


# main

# input
actNum = int(input("NUMBER OF ACTIVITIES : "))
num_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': actNum * 0.3, 'price': actNum * 1.55, 'availability': 0.945 ** actNum, 'reliability': 0.825 ** actNum}
actGraph = generateActGraph(actNum)
candidates = generateCandidates(actNum, num_candidates)


while True :

    mcn = int(input("ITERATION NUMBER : "))
    sq = int(input("SCOUT CONDITION : "))

    paretosList = list()



    print("Executing moabc Algorithm ")
    solutions_moabc = moabc.algorithm(actGraph, candidates,SQ = sq ,MCN=mcn,constraints=constraints)[0]
    paretosList.extend(solutions_moabc)


    print("Executing hybrid Algorithm ")
    solutions_hybrid = hybrid.moabc_nsga2(actGraph, candidates,SQ = sq,MCN=mcn,constraints=constraints)[0]
    paretosList.extend(solutions_hybrid)

    print("Executing nsga2 Algorithm ")
    solutions_nsga2 = nsga2.algorithm(actGraph, candidates,G=mcn,constraints=constraints)[0]
    paretosList.extend(solutions_nsga2)

    print("Finding true pareto ...")
    true_pareto = nonDominatedSort(paretosList)

    # preparing pymoo performance indicators
    if len(solutions_hybrid) > 10 :
        solutions_hybrid = crowdingSort(solutions_hybrid)[:10]

    if len(solutions_nsga2) > 10 :
        solutions_nsga2 = crowdingSort(solutions_nsga2)[:10]

    if len(solutions_moabc) > 10 :
        solutions_moabc = crowdingSort(solutions_moabc)[:10]

    solutions_hybrid = np.array([sol["functions"] for sol in solutions_hybrid])
    solutions_moabc = np.array([sol["functions"] for sol in solutions_moabc])
    solutions_nsga2 = np.array([sol["functions"] for sol in solutions_nsga2])

    true_pareto = np.array([sol["functions"] for sol in true_pareto])

    print("solutions_hybrid")
    print(solutions_hybrid)
    print("+--------------------------------------+")
    print("solutions_moabc")
    print(solutions_moabc)
    print("+--------------------------------------+")
    print("solutions_nsga2")
    print(solutions_nsga2)

    # max objectives in true_pareto
    max = [- inf,- inf,- inf]
    for i in range(3) :
        for x in true_pareto :
            if max[i] < x[i] :
                max[i] = x[i]

    r = np.array([max[0] * 0.9 , max[1] * 0.9 , max[2] * 1.1])

    # evaluating performance
    gd = get_performance_indicator("gd", true_pareto)
    igd = get_performance_indicator("igd", true_pareto)
    hv = get_performance_indicator("hv", ref_point = r)

    # evaluatin MOABC

    GD = gd.calc(solutions_moabc)
    IGD = igd.calc(solutions_moabc)
    HV = hv.calc(solutions_moabc)

    with open('Sequencialdataset.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(["MOABC",actNum,num_candidates,GD,IGD,HV])


    # # evaluating NSGA-II

    GD = gd.calc(solutions_nsga2)
    IGD = igd.calc(solutions_nsga2)
    HV = hv.calc(solutions_nsga2)

    with open('Sequencialdataset.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(["NSGA-II",actNum,num_candidates,GD,IGD,HV])

    # evaluating HYBRID

    GD = gd.calc(solutions_hybrid)
    IGD = igd.calc(solutions_hybrid)
    HV = hv.calc(solutions_hybrid)

    with open('Sequencialdataset.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(["HYBRID",actNum,num_candidates,GD,IGD,HV])
