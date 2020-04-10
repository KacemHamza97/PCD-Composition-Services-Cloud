import csv

from mpl_toolkits.mplot3d import Axes3D
from numpy import array
from time import time

import matplotlib.pyplot as plt
from data_structure.Problem import Problem
from multi_objective_algorithms.algorithms.main.nsga2 import nsga2
from multi_objective_algorithms.algorithms.main.spea2 import spea2
from multi_objective_algorithms.algorithms.main.nsga2_r import nsga2_r
from multi_objective_algorithms.algorithms.main.moabc import moabc
from multi_objective_algorithms.algorithms.main.hybrid import moabc_nsga2
from multi_objective_algorithms.algorithms.operations.update import nonDominatedSort, updateSolutions, transform
from multi_objective_algorithms.experimentation.performance_indicators.performance_indicators import gd , hv , igd

# evaluate and write to CSV file

def evaluate(algorithm , solutions , pf ,  rt) :
    GD = gd(solutions , pf)
    IGD = igd(solutions , pf)
    HV = hv(solutions , pf)

    with open('test_results.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([algorithm , n_act, n_candidates ,mcn , sn , GD ,  IGD , HV , rt])
    

#+----------------------------------------------------------------------------------------------+#    

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
start_time = time()
solutions_moabc = moabc(problem = p , SQ = sq , MCN=mcn ,SN = sn , N = sn // 2)
rt_moabc = time() - start_time


print("Executing hybrid Algorithm ")
start_time = time()
solutions_hybrid = moabc_nsga2(problem = p , SQ = sq , MCN=mcn ,SN = sn , N = sn // 2)
rt_hybrid = time() - start_time

print("Executing nsga2 Algorithm ")
start_time = time()
solutions_nsga2 = nsga2(problem = p , G = mcn ,N = sn)
rt_nsga2 = time() - start_time

print("Executing nsga2_r Algorithm ")
start_time = time()
solutions_nsga2_r = nsga2_r(problem = p , G = mcn ,N = sn , reference_points=array([[-5,-5,3],[-10,-10,1],[-15,-15,2]]) , epsilon = 0.001)
rt_nsga2_r = time() - start_time

print("Executing spea2 Algorithm ")
start_time = time()
solutions_spea2 = spea2(problem = p , G = mcn ,N = sn , EN = 10)
rt_spea2 = time() - start_time

print("Finding true pareto ...")
for itera in range(5) :
    print(f"completed = {(itera + 1) * 100 / 20} %", end='\r')
    paretosList.extend(moabc(problem = p , SQ = sq , MCN=mcn ,SN = sn , N = sn // 2))
    paretosList.extend(nsga2(problem = p , G = mcn ,N = sn ))
    paretosList.extend(nsga2_r(problem = p , G = mcn ,N = sn , reference_points=array([[-5,-5,3],[-10,-10,1],[-15,-15,2]]) , epsilon = 0.001))
    paretosList.extend(spea2(problem = p , G = mcn ,N = sn , EN = 10))
    paretosList.extend(moabc(problem = p , SQ = sq , MCN=mcn ,SN = sn , N = sn // 2))

true_pareto = nonDominatedSort(paretosList)[0]


# evaluating algorithms

print("Evaluating solutions ...")

evaluate(algorithm = "NSGA-II" , solutions = solutions_nsga2 , pf = true_pareto , rt = rt_nsga2)
evaluate(algorithm = "NSGA-II-R" , solutions = solutions_nsga2_r , pf = true_pareto , rt = rt_nsga2_r)
evaluate(algorithm = "SPEA2" , solutions = solutions_spea2 , pf = true_pareto , rt = rt_spea2)
evaluate(algorithm = "MOABC" , solutions = solutions_moabc , pf = true_pareto , rt = rt_moabc)
evaluate(algorithm = "HYBRID" , solutions = solutions_hybrid , pf = true_pareto , rt = rt_hybrid) 

plt.clf()
fig = plt.figure()
ax = Axes3D(fig)
Matrix_true_pareto = transform(true_pareto)
fr1 = Matrix_true_pareto[:, 0]
fr2 = Matrix_true_pareto[:, 1]
fr3 = Matrix_true_pareto[:, 2]

Matrix = transform(solutions_hybrid)
f1 = Matrix[:, 0]
f2 = Matrix[:, 1]
f3 = Matrix[:, 2]

ax.scatter(f1, f2, f3,marker='o')
ax.scatter(fr1, fr2, fr3, marker='^')

ax.set_xlabel('responseTime')
ax.set_ylabel('price')
ax.set_zlabel('availability + reliability')
ax.set_title('Hybrid Algorithm')
plt.savefig(f"3d_plots/3d_plot({n_act},{n_candidates},{mcn},{sn},{sq}).png")
plt.show()