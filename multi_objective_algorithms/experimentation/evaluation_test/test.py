import csv
from numpy import array
from math import inf
from pymoo.factory import get_performance_indicator
import sys
sys.path.append("/users/asus/Desktop/pcd/PCD-COMPOSITION-SERVICES-CLOUD")
from data_structure.Problem import Problem
from multi_objective_algorithms.algorithms.main.nsga2 import nsga2
from multi_objective_algorithms.algorithms.main.spea2 import spea2
from multi_objective_algorithms.algorithms.main.nsga2_r import nsga2_r
from multi_objective_algorithms.algorithms.main.moabc import moabc
from multi_objective_algorithms.algorithms.main.hybrid import moabc_nsga2
from multi_objective_algorithms.algorithms.operations.update import nonDominatedSort , updateSolutions


def evaluate(algorithm , gd , igd , hv , solutions) :
    GD = gd.calc(solutions)
    IGD = igd.calc(solutions)
    HV = hv.calc(solutions)

    with open('test_results.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([algorithm , n_candidates , GD , IGD , HV])
    
    

# main

# input
n_act = int(input("NUMBER OF ACTIVITIES : "))
n_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': n_act * 0.3, 'price': n_act * 1.55, 'availability': 0.945 ** n_act, 'reliability': 0.825 ** n_act}

mcn = int(input("ITERATION NUMBER / GENERATIONS NUMBER : "))
sn = int(input("RESSOURCES NUMBER / POPULATION SIZE : "))
sq = int(input("SCOUT CONDITION : "))

# problem init

p = Problem(n_act, n_candidates, constraints)


# executing algorithms

paretosList = list()


print("Executing moabc Algorithm ")
solutions_moabc = moabc(problem = p , SQ = sq , MCN=mcn ,SN = sn , N = sn // 2)
paretosList.extend(solutions_moabc)


print("Executing hybrid Algorithm ")
solutions_hybrid = moabc_nsga2(problem = p , SQ = sq , MCN=mcn ,SN = sn , N = sn // 2)
paretosList.extend(solutions_hybrid)

print("Executing nsga2 Algorithm ")
solutions_nsga2 = nsga2(problem = p , G = mcn ,N = sn , CP = 0.2 , CM = 0.1)
paretosList.extend(solutions_nsga2)

print("Executing nsga2_r Algorithm ")
solutions_nsga2_r = nsga2_r(problem = p , G = mcn ,N = sn , CP = 0.2 , CM = 0.1 , reference_points=[(1,1,1),(1,1,1),(1,1,1)])
paretosList.extend(solutions_nsga2)

print("Executing spea2 Algorithm ")
solutions_spea2 = spea2(problem = p , G = mcn ,N = sn , EN = 10)
paretosList.extend(solutions_spea2)

print("Finding true pareto ...")
true_pareto = nonDominatedSort(paretosList)[0]

# showing results

solutions_hybrid = array([sol.functions for sol in solutions_hybrid])
solutions_moabc = array([sol.functions for sol in solutions_moabc])
solutions_nsga2 = array([sol.functions for sol in solutions_nsga2])
solutions_nsga2_r = array([sol.functions for sol in solutions_nsga2_r])
solutions_spea2 = array([sol.functions for sol in solutions_spea2])

true_pareto = array([sol.functions for sol in true_pareto])

print("true_pareto")
print(true_pareto)
print("+--------------------------------------+")
print("solutions_hybrid")
print(solutions_hybrid)
print("+--------------------------------------+")
print("solutions_moabc")
print(solutions_moabc)
print("+--------------------------------------+")
print("solutions_nsga2")
print(solutions_nsga2)
print("+--------------------------------------+")
print("solutions_nsga2_r")
print(solutions_nsga2_r)
print("+--------------------------------------+")
print("solutions_spea2")
print(solutions_spea2)

# max objectives in true_pareto
max = [- inf,- inf,- inf]
for i in range(3) :
    for x in true_pareto :
        if max[i] < x[i] :
            max[i] = x[i]

r = array([max[0] * 0.9 , max[1] * 0.9 , max[2] * 1.1])

# evaluating performance
gd = get_performance_indicator("gd", true_pareto)
igd = get_performance_indicator("igd", true_pareto)
hv = get_performance_indicator("hv", ref_point = r)

# evaluating algorithms

evaluate(algorithm = "NSGA-II" , gd = gd , igd = igd , hv = hv , solutions = solutions_nsga2)
evaluate(algorithm = "NSGA-II-R" , gd = gd , igd = igd , hv = hv , solutions = solutions_nsga2_r)
evaluate(algorithm = "SPEA2" , gd = gd , igd = igd , hv = hv , solutions = solutions_spea2)
evaluate(algorithm = "MOABC" , gd = gd , igd = igd , hv = hv , solutions = solutions_moabc)
evaluate(algorithm = "HYBRID" , gd = gd , igd = igd , hv = hv , solutions = solutions_hybrid)

    
