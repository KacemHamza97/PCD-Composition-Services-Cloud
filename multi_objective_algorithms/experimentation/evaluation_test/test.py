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


def plot_5(true_pareto, sol_hybrid, sol_moabc, sol_spea2, sol_nsga2):
    plt.clf()
    fig1 = plt.figure()
    ax = Axes3D(fig1)

    ftp1, ftp2, ftp3 = plot_fx(true_pareto)
    fh1, fh2, fh3 = plot_fx(sol_hybrid)
    fm1, fm2, fm3 = plot_fx(sol_moabc)
    fsp1, fsp2, fsp3 = plot_fx(sol_spea2)
    fns1, fns2, fns3 = plot_fx(sol_nsga2)

    ax.scatter(ftp1, ftp2, ftp3, marker='^', label='True pareto')
    ax.scatter(fh1, fh2, fh3, marker='o', label='HYBRID')
    ax.scatter(fm1, fm2, fm3, marker='s', label='MOABC')
    ax.scatter(fsp1, fsp2, fsp3, marker='*', label='SPEA2')
    ax.scatter(fns1, fns2, fns3, marker='+', label='NSGA-II')

    ax.set_xlabel('responseTime')
    ax.set_ylabel('price')
    ax.set_zlabel('availability + reliability')
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
    ax.set_zlabel('availability + reliability')
    ax.legend()
    plt.savefig(f"plots/plot_{algorithm}({n_act},{n_candidates},{mcn},{sn},{sq}).png")


# +----------------------------------------------------------------------------------------------+#

def evaluate(algorithm, solutions, pf, rt):
    GD = gd(solutions, pf)
    IGD = igd(solutions, pf)
    HV = hv(solutions, pf)

    with open('test_results.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([algorithm, n_act, n_candidates, mcn, sn, GD, IGD, HV, rt])


# +----------------------------------------------------------------------------------------------+#

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
solutions_moabc = moabc(problem=p, SQ=sq, MCN=mcn, SN=sn, N=sn // 2)
rt_moabc = time() - start_time

print("Executing hybrid Algorithm ")
start_time = time()
solutions_hybrid = moabc_nsga2(problem=p, SQ=sq, MCN=mcn, SN=sn, N=sn // 2)
rt_hybrid = time() - start_time

print("Executing nsga2 Algorithm ")
start_time = time()
solutions_nsga2 = nsga2(problem=p, G=mcn, N=sn)
rt_nsga2 = time() - start_time

print("Executing nsga2_r Algorithm ")
start_time = time()
solutions_nsga2_r = nsga2_r(problem=p, G=mcn, N=sn, reference_points=array([[-5, -5, 3], [-10, -10, 1], [-15, -15, 2]]), epsilon=0.001)
rt_nsga2_r = time() - start_time

print("Executing spea2 Algorithm ")
start_time = time()
solutions_spea2 = spea2(problem=p, G=mcn, N=sn, EN=10)
rt_spea2 = time() - start_time

print("Finding true pareto ...")
for itera in range(10):
    print(f"completed = {(itera + 1) * 100 / 20} %", end='\r')
    paretosList.extend(moabc(problem=p, SQ=sq, MCN=mcn, SN=sn, N=sn // 2))
    paretosList.extend(nsga2(problem=p, G=mcn, N=sn))
    paretosList.extend(nsga2_r(problem=p, G=mcn, N=sn, reference_points=array([[-5, -5, 3], [-10, -10, 1], [-15, -15, 2]]), epsilon=0.001))
    paretosList.extend(spea2(problem=p, G=mcn, N=sn, EN=10))
    paretosList.extend(moabc(problem=p, SQ=sq, MCN=mcn, SN=sn, N=sn // 2))

true_pareto = nonDominatedSort(paretosList)[0]

# evaluating algorithms

print("Evaluating solutions ...")

evaluate(algorithm="NSGA-II", solutions=solutions_nsga2, pf=true_pareto, rt=rt_nsga2)
evaluate(algorithm="NSGA-II-R", solutions=solutions_nsga2_r, pf=true_pareto, rt=rt_nsga2_r)
evaluate(algorithm="SPEA2", solutions=solutions_spea2, pf=true_pareto, rt=rt_spea2)
evaluate(algorithm="MOABC", solutions=solutions_moabc, pf=true_pareto, rt=rt_moabc)
evaluate(algorithm="HYBRID", solutions=solutions_hybrid, pf=true_pareto, rt=rt_hybrid)

reference_points = array([[-5, -5, 3], [-10, -10, 1], [-15, -15, 2]])

# plot_3(true_pareto, solutions_moabc, 'MOABC', solutions_hybrid)
# plot_algo(true_pareto,solutions_nsga2_r,'NSGA-II-R',solutions_hybrid,reference_points=reference_points)
plot_5(true_pareto, solutions_hybrid, solutions_moabc, solutions_spea2, solutions_nsga2)