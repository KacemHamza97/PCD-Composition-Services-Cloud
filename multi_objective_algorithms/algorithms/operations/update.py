
from multi_objective_algorithms.algorithms.operations.objective_functions import functions , fit , dominates

#+----------------------------------------------------------------------------------------------+#


def nonDominatedSort(solutionsList) :
        fronts = [[]]   
        SList = {}    
        NList = {} 
        for sol1 in solutionsList :
            Sp = list()   # list of solutions dominated by sol1
            Np = 0        # number of solutions which dominate sol1
            for sol2 in solutionsList :
                if dominates(sol1 , sol2) : 
                    Sp.append(sol2)
                elif dominates(sol2 , sol1) : 
                    Np += 1
            if Np == 0 :  
                fronts[0].append(sol1)   # pareto front
            SList[sol1] = Sp 
            NList[sol1] = Np

        i = 0  # front number 
        # updating fronts
        while len(fronts[i]) != 0 :
            f = []
            for sol1 in fronts[i] : 
                for sol2 in SList[sol1] :
                    NList[sol2] -= 1      # exclude ith front
                    if NList[sol2] == 0 : # sol2 no longer dominated
                        f.append(sol2)    # added to the next front
            i += 1
            fronts.append(f)

        return fronts


#+----------------------------------------------------------------------------------------------+#


def crowdingSort(front , dimensions) :
    scoresList = list()
    for sol1 in front :
        score = list() # score of sol1
        for d in range(dimensions) :
            high = []    # solutions with higher value in dimension d
            low =  []    # solutions with lower value in dimension  d
            for sol2 in front :
                if sol2.functions[d] < sol1.functions[d]  :  # lower value found
                    low.append(sol2.functions[d])
                if sol2.functions[d] > sol1.functions[d] :   # heigher value found
                    high.append(sol2.functions[d])
            if len(high) == 0 :  # no heigher value found
                next_high = sol1.functions[d]
            else :
                next_high = min(high)  # smallest heigher value
            if len(low) == 0 :   # no lower value found
                next_low = sol1.functions[d]
            else :
                next_low = max(low)    # biggest lower value
            score.append((next_high-next_low)/(max(high) - min(low))) # normalized score
        scoresList.append(sum(score))

    # returning front sorted by DESC order based on crowdingScores
    return [x[1] for x in sorted(zip(scoresList , front) , key = lambda x:x[0] , reverse = True)]



#+----------------------------------------------------------------------------------------------+#


def updateSolutions(solutionsList , fronts , method) :
    i = 0   # front number
    S = []  # new solutionsList
    N = len(solutionsList)

    while i < len(fronts) and len(fronts[i]) <= N - len(S) : 
        # add fronts to S until space left is lower than front size
        S += fronts[i]
        i += 1

    if i < len(fronts) : 
        # selecting solutions from front based on method
        if method == "crowdingSort" :
            selection = crowdingSort(solutionsList , fronts[i])[0:N - len(S)]
            S += selection

    for sol in S :
        sol.fitness = fit(sol,solutionsList)
        if sol in solutionsList : 
            sol.limit += 1
        
    return S