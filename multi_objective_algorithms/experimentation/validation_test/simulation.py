import networkx
import matplotlib.pyplot as plt
from data_structure.Problem import Problem
from multi_objective_algorithms.experimentation.validation_test.hybrid import simMoabc_nsga2


# main

# input
# input
n_act = 5
n_candidates = 50
constraints = {'responseTime': n_act * 5 , 'price': n_act * 3, 'availability': 0.9 ** n_act, 'reliability': 0.7 ** n_act}
mcn = 10
sq = 2
sn = 10

# problem init

p = Problem(n_act , n_candidates , constraints)

# plotting simulation actGraph

positions = {0: [0, 0], 1: [1, 0], 2: [2, 0] , 3: [3, 0], 4: [4, 0]}
G = networkx.DiGraph()
G.add_weighted_edges_from(p.getActGraph())
networkx.drawing.nx_pylab.draw_networkx(G, pos=positions)
plt.show()

# executing simulation
simMoabc_nsga2(problem = p,SQ=sq ,MCN=mcn,SN = sn , N = sn // 2)
