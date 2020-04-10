from pymoo.factory import get_performance_indicator
from multi_objective_algorithms.algorithms.operations.update import normalize , transform , normalized_Euclidean_Distance
from numpy import array

#+----------------------------------------------------------------------------------------------+#

def euclidean_distance (a , b , norm) : 
    return (( (a - b) / norm ) ** 2).sum(axis = 0) ** 0.5

#+----------------------------------------------------------------------------------------------+#

def gd(solutions , pf) :

    norm = normalize(transform(pf))

    D = array([min([euclidean_distance(sol , p , norm) for p in transform(pf)]) for sol in transform(solutions)])

    return ((D ** 2).sum(axis = 0) ** 0.5) / len(solutions)



#+----------------------------------------------------------------------------------------------+#

def igd(solutions , pf) : 
    return gd(pf , solutions)

#+----------------------------------------------------------------------------------------------+#

def hv(solutions , pf) : 
    indicator = get_performance_indicator("hv" , pf = transform(pf) , normalize = True)
    return indicator.calc(transform(solutions))

