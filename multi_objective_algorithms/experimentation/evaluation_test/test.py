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
from multi_objective_algorithms.algorithms.operations.update import nonDominatedSort, transform
from multi_objective_algorithms.experimentation.performance_indicators.performance_indicators import gd, hv, igd


# +----------------------------------------------------------------------------------------------+#
def plot_fx(solutions):
    try:
        Matrix = transform(solutions)
    except:
        Matrix = solutions
    f1 = Matrix[:, 0]
    f2 = Matrix[:, 1]
    f3 = Matrix[:, 2]
    return f1, f2, f3


def plot_5(true_pareto, sol_hybrid, sol_moabc, sol_spea2, sol_nsga2, sol_nsga2_r):
    plt.clf()
    fig1 = plt.figure()
    ax = Axes3D(fig1)

    ftp1, ftp2, ftp3 = plot_fx(true_pareto)
    fh1, fh2, fh3 = plot_fx(sol_hybrid)
    fm1, fm2, fm3 = plot_fx(sol_moabc)
    fsp1, fsp2, fsp3 = plot_fx(sol_spea2)
    fns1, fns2, fns3 = plot_fx(sol_nsga2)
    fnr1, fnr2, fnr3 = plot_fx(sol_nsga2)

    ax.scatter(ftp1, ftp2, ftp3, marker='^', label='True pareto')
    ax.scatter(fh1, fh2, fh3, marker='o', label='HYBRID')
    ax.scatter(fm1, fm2, fm3, marker='s', label='MOABC')
    ax.scatter(fsp1, fsp2, fsp3, marker='*', label='SPEA2')
    ax.scatter(fns1, fns2, fns3, marker='+', label='NSGA-II')
    ax.scatter(fnr1, fnr2, fnr3, marker='+', label='NSGA-II-R')

    ax.set_xlabel('responseTime')
    ax.set_ylabel('price')
    ax.set_zlabel('reliability')
    ax.legend()
    plt.savefig(f"plots/plot_all({n_act},{n_candidates},{mcn},{sn},{sq}).png")


def plot_3(true_pareto, solutions, algorithm, hybrid_sol, reference_points=None):
    plt.clf()
    ftp1, ftp2, ftp3 = plot_fx(true_pareto)
    f1, f2, f3 = plot_fx(solutions)
    fig1 = plt.figure()
    ax = Axes3D(fig1)
    ax.scatter(ftp1, ftp2, ftp3, marker='^', label='True pareto')
    ax.scatter(f1, f2, f3, marker='o', label=algorithm)
    if algorithm != 'NSGA-II-R':
        fh1, fh2, fh3 = plot_fx(hybrid_sol)
        ax.scatter(fh1, fh2, fh3, marker='s', label='Hybrid')
    else:
        rf1, rf2, rf3 = plot_fx(reference_points)
        ax.scatter(rf1, rf2, rf3, marker='s', label='reference points')

    ax.set_xlabel('responseTime')
    ax.set_ylabel('price')
    ax.set_zlabel('reliability')
    ax.legend()
    plt.savefig(f"plots/plot_{algorithm}({n_act},{n_candidates},{mcn},{sn},{sq}).png")


# +----------------------------------------------------------------------------------------------+#

def evaluate(algorithm, pf, **kwargs):
    HV_list = []
    GD = 0
    IGD = 0
    rt = 0
    solutions = []
    for i in range(30):
        print(f"Executing hybrid {algorithm.__name__} ")
        start_time = time()
        solutions = algorithm(problem=p, **kwargs)
        rt += (time() - start_time) / 30
        GD += gd(solutions, pf) / 30
        IGD += igd(solutions, pf) / 30
        HV = hv(solutions, pf)
        HV_list.append(HV)

        ##### USED TO GENERATE DATA FOR BOXPLOTS ######################################################
        #with open('hv_abstract.csv', mode='a') as file:
        #    file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #    file_writer.writerow([algorithm.__name__, n_act, HV])
        #with open('hv_concrete.csv', mode='a') as file:
        #    file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #    file_writer.writerow([algorithm.__name__, n_candidates, HV])
        ###############################################################################################

    HV = sum(HV_list) / 30
    HV_min = min(HV_list)
    HV_max = max(HV_list)
    with open('test_results.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([algorithm.__name__, n_act, n_candidates, mcn, sn, GD, IGD, HV, HV_min , HV_max, rt])

    return solutions


# +----------------------------------------------------------------------------------------------+#

# main

# input
n_act = int(input("NUMBER OF ACTIVITIES : "))
n_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': n_act * 0.3, 'price': n_act * 1.55, 'availability': 0.945 ** n_act, 'reliability': 0.825 ** n_act}
reference_points = array([[-5, -5, 3], [-10, -10, 1], [-15, -15, 2]])
mcn = int(input("ITERATION NUMBER / GENERATIONS NUMBER : "))
sn = int(input("RESSOURCES NUMBER / POPULATION SIZE : "))
sq = int(input("SCOUT CONDITION : "))

# problem init

p = Problem(n_act, n_candidates, constraints)

# executing algorithms

paretosList = list()
print("Finding true pareto ...")
for itera in range(30):
    print(f"completed = {(itera + 1) * 100 / 30} %", end='\r')
    paretosList.extend(moabc(problem=p, SQ=sq, MCN=mcn, SN=sn, N=sn // 2))
    paretosList.extend(nsga2(problem=p, G=mcn, N=sn))
    paretosList.extend(nsga2_r(problem=p, G=mcn, N=sn, reference_points=reference_points, epsilon=0.001))
    paretosList.extend(spea2(problem=p, G=mcn, N=sn, EN=10))
    paretosList.extend(moabc(problem=p, SQ=sq, MCN=mcn, SN=sn, N=sn // 2))

true_pareto = nonDominatedSort(paretosList)[0]

# evaluating algorithms
print("Evaluating solutions ...")
solutions_nsga2 = evaluate(algorithm=nsga2, pf=true_pareto, G=mcn, N=sn)
solutions_nsga2_r = evaluate(algorithm=nsga2_r, pf=true_pareto, G=mcn, N=sn, reference_points=reference_points, epsilon=0.001)
solutions_spea2 = evaluate(algorithm=spea2, pf=true_pareto, G=mcn, N=sn, EN=10)
solutions_moabc = evaluate(algorithm=moabc, pf=true_pareto, SQ=sq, MCN=mcn, SN=sn, N=sn // 2)
solutions_hybrid = evaluate(algorithm=moabc_nsga2, pf=true_pareto, SQ=sq, MCN=mcn, SN=sn, N=sn // 2)

plot_3(true_pareto, solutions_moabc, 'MOABC', solutions_hybrid)
plot_3(true_pareto, solutions_spea2, 'SPEA2', solutions_hybrid)
plot_3(true_pareto, solutions_nsga2, 'NSGA-II', solutions_hybrid)
plot_3(true_pareto, solutions_nsga2_r, 'NSGA-II-R', solutions_hybrid, reference_points=reference_points)
plot_5(true_pareto, solutions_hybrid, solutions_moabc, solutions_spea2, solutions_nsga2, solutions_nsga2_r)
