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
from multi_objective_algorithms.algorithms.main.hybrid_v0 import moabc_nsga2_v0
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
    fnr1, fnr2, fnr3 = plot_fx(sol_nsga2_r)

    ax.scatter(ftp1 * -1 , ftp2 * -1 , ftp3, marker='^', label='True pareto')
    ax.scatter(fh1 * -1 , fh2 * -1 , fh3, marker='o', label='HYBRID')
    ax.scatter(fm1 * -1 , fm2 * -1 , fm3, marker='s', label='MOABC')
    ax.scatter(fsp1 * -1 , fsp2 * -1 , fsp3, marker='*', label='SPEA2')
    ax.scatter(fns1 * -1 , fns2 * -1 , fns3, marker='+', label='NSGA-II')
    ax.scatter(fnr1 * -1 , fnr2 * -1 , fnr3, marker='x', label='NSGA-II-R')

    ax.set_xlabel('responseTime')
    ax.set_ylabel('price')
    ax.set_zlabel('reliability')
    ax.legend()
    plt.savefig(f"plots/plot_all({n_act},{n_candidates},{mcn},{sn},{sq}).png")


def plot_3(true_pareto, solutions, algorithm, hybrid_sol, reference_points=None , neighbors = None):
    plt.clf()
    fig1 = plt.figure()
    ax = Axes3D(fig1)
    ftp1, ftp2, ftp3 = plot_fx(true_pareto)
    fh1, fh2, fh3 = plot_fx(hybrid_sol)
    ax.scatter(fh1 * -1 , fh2 * -1 , fh3, marker='s', label='Hybrid')
    ax.scatter(ftp1 * -1 , ftp2 * -1 , ftp3, marker='^', label='True pareto')
    if algorithm != 'NSGA-II-R':
        f1, f2, f3 = plot_fx(solutions)
        ax.scatter(f1 * -1 , f2 * -1 , f3, marker='o', label=algorithm)
    else :
        rf1, rf2, rf3 = plot_fx(reference_points)
        rn1, rn2, rn3 = plot_fx(neighbors)
        further_points = []
        for sol1 in solutions :
            if sol1.cp not in [sol2.cp for sol2 in neighbors] :
                further_points.append(sol1)
        if len(further_points) != 0 :
            f1, f2, f3 = plot_fx(further_points)
            ax.scatter(rn1 * -1 , rn2 * -1 , rn3, marker='d', label='neighboring points')
            ax.scatter(f1 * -1 , f2 * -1 , f3, marker='o', label='rest of solutions')

        ax.scatter(rf1 * -1 , rf2 * -1 , rf3, marker='s', label='reference points')

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
    for i in range(10):
        print(f"Executing {algorithm.__name__} ")
        start_time = time()
        if algorithm == nsga2_r :
            solutions , neighbors = algorithm(problem=p, **kwargs)
        else :
            solutions = algorithm(problem=p, **kwargs)
        rt += (time() - start_time) / 10
        GD += gd(solutions, pf) / 10
        IGD += igd(solutions, pf) / 10
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

    HV = sum(HV_list) / 10
    HV_min = min(HV_list)
    HV_max = max(HV_list)
    with open('test_results.csv', mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow([algorithm.__name__, n_act, n_candidates, mcn, sn, GD, IGD, HV, HV_min , HV_max, rt])

    if algorithm == nsga2_r:
        return solutions , neighbors
    else :
        return solutions


# +----------------------------------------------------------------------------------------------+#

# main

# input
n_act = int(input("NUMBER OF ACTIVITIES : "))
n_candidates = int(input("NUMBER OF CANDIDATE SERVICES : "))
constraints = {'responseTime': n_act * 2 , 'price': n_act * 3, 'availability': 0.92 ** n_act, 'reliability': 0.75 ** n_act}
reference_points = array([[-10, -10, 0.9], [-3, -5, 0.7], [-5, -3, 0.7]])
mcn = int(input("ITERATION NUMBER / GENERATIONS NUMBER : "))
sn = int(input("RESSOURCES NUMBER / POPULATION SIZE : "))
sq = int(input("SCOUT CONDITION : "))
en = int(input("ARCHIVE SIZE :"))
# problem init

p = Problem(n_act, n_candidates, constraints)

# executing algorithms

paretosList = list()
print("Finding true pareto ...")
for itera in range(10):
    print(f"completed = {itera + 1}/ 10" )
    print(f"MOABC")
    paretosList.extend(moabc(problem=p, SQ=sq, MCN=mcn, SN=sn, N= sn // 2))
    print(f"NSGA2")
    paretosList.extend(nsga2(problem=p, G=mcn, N=sn))
    #print(f"NSGA2-R")
    #paretosList.extend(nsga2_r(problem=p, G=mcn, N=sn, reference_points=reference_points, epsilon=0.2)[0])
    #print(f"SPEA2")
    #paretosList.extend(spea2(problem=p, G=mcn, N=sn, EN=en))
    print(f"HYBRID")
    paretosList.extend(moabc_nsga2_v0(problem=p, SQ=sq, MCN=mcn, SN=sn, N= sn // 2))

true_pareto = nonDominatedSort(paretosList)[0]

# evaluating algorithms
print("Evaluating solutions ...")
solutions_nsga2 = evaluate(algorithm=nsga2, pf=true_pareto, G=mcn, N=sn)
#solutions_nsga2_r , neighbors = evaluate(algorithm=nsga2_r, pf=true_pareto, G=mcn, N=sn, reference_points=reference_points, epsilon=0.2)
#solutions_spea2 = evaluate(algorithm=spea2, pf=true_pareto, G=mcn, N=sn, EN = en)
solutions_moabc = evaluate(algorithm=moabc, pf=true_pareto, SQ=sq, MCN=mcn, SN=sn, N= sn // 2)
solutions_hybrid = evaluate(algorithm=moabc_nsga2_v0, pf=true_pareto, SQ=sq, MCN=mcn, SN=sn, N= sn // 2)


plot_3(true_pareto, solutions_moabc, 'MOABC', solutions_hybrid)
#plot_3(true_pareto, solutions_spea2, 'SPEA2', solutions_hybrid)
plot_3(true_pareto, solutions_nsga2, 'NSGA-II', solutions_hybrid)
#plot_3(true_pareto, solutions_nsga2_r,'NSGA-II-R', solutions_hybrid, reference_points=reference_points,neighbors = neighbors)
#plot_5(true_pareto, solutions_hybrid, solutions_moabc, solutions_spea2, solutions_nsga2, solutions_nsga2_r)
