import time
import csv
import sys
from numpy import array
path = "/Users/asus/Desktop/pcd/PCD-Composition-Services-Cloud"
sys.path.append(path)

from data_structure.Problem import Problem
from mono_objective_algorithms.algorithms.main.hybrid import ABCgenetic
from mono_objective_algorithms.algorithms.main.ABC import ABC
from mono_objective_algorithms.algorithms.main.genetic import genetic
from mono_objective_algorithms.algorithms.operations.fitness import fit

def evaluate(algorithm , **kwargs) :
    rt_list = []
    cp_list = []
    min_list = []
    max_list = []
    conv_list = []
    for itera in range(30) : 
        print(f"Executing Algorithm : {algorithm.__name__} {itera+1}/30")
        start_time = time.time()
        result, minQos, maxQos , conv_itera = algorithm(**kwargs)
        rt = time.time() - start_time
        rt_list.append(rt)
        print(rt)
        min_list.append(minQos)
        max_list.append(maxQos)
        cp_list.append(result)
        conv_list.append(conv_itera)

    minQos_avg = {qos : sum([cp_qos[qos] / 30 for cp_qos in min_list]) for qos in opt.cpQos().keys()}
    maxQos_avg = {qos : sum([cp_qos[qos] / 30 for cp_qos in max_list]) for qos in opt.cpQos().keys()}
    fit_list = [fit(cp , minQos_avg , maxQos_avg , weights) for cp in cp_list ]
    fit_avg = sum(fit_list) / 30
    rt_avg = sum(rt_list) / 30
    opt_fit = fit(opt , minQos_avg , maxQos_avg , weights)
    div = 0
    conv = sum(conv_list) / 30
    for i in range(len(fit_list)-1) : 
        div += abs( fit_list[i+1] - fit_list[i] ) / 29

    with open('./mono_objective_algorithms/experimentation/evaluation_test/test_results.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if (algorithm.__name__ == "ABCgenetic" or "ABC") :
            file_writer.writerow([algorithm.__name__,n_act, n_candidates, sn,mcn ,sq, fit_avg / opt_fit, rt_avg , div , conv])
        else :
            file_writer.writerow([algorithm.__name__,n_act, n_candidates, sn,mcn ,'Nan', fit_avg / opt_fit, rt_avg , div , conv])
# main

# input
n_act = int(input("NUMBER OF ACTIVITIES : "))
n_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': n_act * 0.3, 'price': n_act * 1.55, 'availability': 0.945 ** n_act,
               'reliability': 0.825 ** n_act}
weights = [0.25, 0.25, 0.25, 0.25]
mcn = int(input("ITERATION NUMBER / GENERATION NUMBER : "))
sn = int(input("RESSOURCES NUMBER / POPULATION SIZE : "))
sq = int(input("SCOUTS CONDITION : "))


# problem init

p = Problem(n_act , n_candidates , constraints , weights)

# optimal fitness

print("optimal fitness search !")
opt, _, _ , _ = ABCgenetic(problem = p, SN=sn, SQ=100, MCN=mcn * 10,SCP=9 * mcn // 10, N=sn // 2,CP=0.2)
print("\nDone !")

# test scenarios

evaluate(ABCgenetic , problem = p, SN=sn, SQ=sq, MCN=mcn,SCP=9 * mcn // 10, N=sn // 2 , CP=0.2)
evaluate(ABC , problem = p, SN=sn, SQ=sq, MCN=mcn , N=sn // 2)
evaluate(genetic , problem = p, N = sn , G = mcn , CP = 0.75, CM = 0.1)
