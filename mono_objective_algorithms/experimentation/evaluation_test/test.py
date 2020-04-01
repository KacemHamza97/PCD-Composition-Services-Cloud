import time
import csv
import sys
path = "/Users/asus/Desktop/pcd/PCD-Composition-Services-Cloud"
sys.path.append(path)

from data_structure.Problem import Problem
from mono_objective_algorithms.algorithms.main.hybrid import ABCgenetic
from mono_objective_algorithms.algorithms.main.ABC import ABC
from mono_objective_algorithms.algorithms.main.genetic import genetic
from mono_objective_algorithms.algorithms.operations.fitness import fit

def evaluate(algorithm , **kwargs) :
    rt = 0
    fit_prev = 0
    div = 0
    conv = []
    normalized_fitness = 0
    for itera in range(30) : 
        print(f"Executing Algorithm : {algorithm.__name__} {itera+1}/30")
        start_time = time.time()
        result, minQos, maxQos = algorithm(**kwargs)
        rt += (time.time() - start_time) / 30
        normalized_fitness += (fit(result, minQos, maxQos, weights) / fit(opt, minQos, maxQos, weights)) / 30
        div += abs(fit(result, minQos, maxQos, weights)-fit_prev) / 30
        fit_prev = fit(result, minQos, maxQos, weights)
        if fit(result, minQos, maxQos, weights)-fit_prev ==0 :
            conv.append(itera+1)

    with open('./mono_objective_algorithms/experimentation/evaluation_test/test_results.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([algorithm.__name__,n_act, n_candidates, sn, sq, mcn, normalized_fitness, rt,div,conv])

# main

# input
n_act = int(input("NUMBER OF ACTIVITIES : "))
n_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': n_act * 0.3, 'price': n_act * 1.55, 'availability': 0.945 ** n_act,
               'reliability': 0.825 ** n_act}
weights = [0.25, 0.25, 0.25, 0.25]
mcn = int(input("ITERATION NUMBER : "))
sn = int(input("RESSOURCES NUMBER : "))
sq = int(input("SCOUTS CONDITION : "))


# problem init

p = Problem(n_act , n_candidates , constraints , weights)

# optimal fitness

print("optimal fitness search !")
opt, _, _ = ABCgenetic(problem = p, SN=sn, SQ=100, MCN=mcn * 10,SCP=9 * mcn // 10, N=sn // 2,CP=0.2)
print("\nDone !")

# test scenarios

evaluate(ABCgenetic , problem = p, SN=sn, SQ=100, MCN=mcn * 10,SCP=9 * mcn // 10, N=sn // 2,CP=0.2)
evaluate(ABC , problem = p, SN=sn, SQ=100, MCN=mcn , N=sn // 2)
evaluate(genetic , problem = p, N = sn , G = mcn , CP = 0.75, CM = 0.1)
