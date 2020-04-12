from pymoo.factory import get_performance_indicator
from multi_objective_algorithms.algorithms.operations.update import normalize , transform , normalized_Euclidean_Distance
from numpy import array

#+----------------------------------------------------------------------------------------------+#

def gd(solutions , pf) :

    norm = normalize(transform(pf))

    D = array([min([normalized_Euclidean_Distance(sol , p , norm) for p in transform(pf)]) for sol in transform(solutions)])

    return ((D ** 2).sum(axis = 0) ** 0.5) / len(solutions)



#+----------------------------------------------------------------------------------------------+#

def igd(solutions , pf) : 
    return gd(pf , solutions)

#+----------------------------------------------------------------------------------------------+#

def hv(solutions , pf) :
    indicator = get_performance_indicator("hv" , pf = transform(pf) , normalize = True)
    return indicator.calc(transform(solutions))
