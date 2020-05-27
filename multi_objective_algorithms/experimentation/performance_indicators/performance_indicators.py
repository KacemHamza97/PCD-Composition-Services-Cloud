from pymoo.factory import get_performance_indicator
from multi_objective_algorithms.algorithms.operations.update import normalize, transform, normalized_Euclidean_Distance
from numpy import array


# +----------------------------------------------------------------------------------------------+#

def gd(solutions, pf):
    norm = normalize(transform(pf))

    D = array(
        [min([normalized_Euclidean_Distance(sol, p, norm) for p in transform(pf)]) for sol in transform(solutions)])

    return ((D ** 2).sum(axis=0) ** 0.5) / len(solutions)


# +----------------------------------------------------------------------------------------------+#

def igd(solutions, pf):
    return gd(pf, solutions)


# +----------------------------------------------------------------------------------------------+#

def hv(solutions, pf):
    indicator = get_performance_indicator("hv", pf=transform(pf) * -1, normalize=True)
    return indicator.calc(transform(solutions) * -1)  # Max optimization problem


# +----------------------------------------------------------------------------------------------+#

def spread(solutions, pf):
    M = 3

    Max_solutions = []
    Max_pareto = []
    Min_solutions = []
    Min_pareto = []

    for i in range(M):
        Max_solutions.append(max([sol[i] for sol in transform(solutions)]))
        Min_solutions.append(min([sol[i] for sol in transform(solutions)]))
        Max_pareto.append(max([sol[i] for sol in transform(pf)]))
        Min_pareto.append(min([sol[i] for sol in transform(pf)]))

    S = 0
    for i in range(M):
        S += ((min(Max_solutions[i], Max_pareto[i]) - max(Min_solutions[i], Min_pareto[i])) / Max_pareto[i] -
              Min_pareto[i]) ** 2

    return (S / M) ** 0.5


# +----------------------------------------------------------------------------------------------+#

def spacing(solutions, pf):
    norm = normalize(transform(pf))

    n = len(solutions)

    di = array(
        [min([normalized_Euclidean_Distance(sol, p, norm) for p in transform(pf)]) for sol in transform(solutions)])

    d = di.sum(axis=0) / n

    return (((di - d) ** 2).sum(axis=0) / n) ** 0.5
