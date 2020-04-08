
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


def crowdingSort(front) :
    if len(front) > 2 :
        scoresList = list()
        for sol1 in front :
            score = list() # score of sol1
            for d in range(3) :
                high = []    # solutions with higher value in dimension d
                low =  []    # solutions with lower value in dimension  d
                for sol2 in front :
                    if sol2.functions[d] < sol1.functions[d]  :  # lower value found
                        low.append(sol2.functions[d])
                    if sol2.functions[d] > sol1.functions[d] :   # heigher value found
                        high.append(sol2.functions[d])
                if len(high) == 0 :  # no heigher value found
                    next_high = sol1.functions[d]
                    high.append(next_high)
                else :
                    next_high = min(high)  # smallest heigher value
                if len(low) == 0 :   # no lower value found
                    next_low = sol1.functions[d]
                    low.append(next_low)
                else :
                    next_low = max(low)    # biggest lower value
                
                # Making sure max_d != min_d
                max_d = max(high)
                min_d = min(low)
                if max_d == min_d : 
                    max_d = 1
                    min_d = 0

                score.append((next_high-next_low)/( max_d - min_d)) # normalized score
            scoresList.append(sum(score))

        # returning front sorted by DESC order based on crowdingScores
        return [x[1] for x in sorted(zip(scoresList , front) , key = lambda x:x[0] , reverse = True)]
    
    else :
        return front



#+----------------------------------------------------------------------------------------------+#


def normalized_Euclidean_Distance(sol1 , reference_point , min_list , max_list) :
    S = 0
    for d in range(3) :
        S += ((sol1.functions[d] - reference_point[d]) / (max_list[d] - min_list[d])) ** 2

    return S ** 0.5



#+----------------------------------------------------------------------------------------------+#


def referencePoints(front , reference_points) :
    if len(front) > 1 :
        min_list = []
        max_list = []
        for d in range(3) :
            # Finding f_min and f_max for d-dimension
            f_min = front[0].functions[d]
            f_max = front[0].functions[d]
            for sol2 in front : 
                if sol2.functions[d] < f_min :
                    f_min = sol2.functions[d]
                if sol2.functions[d] > f_max :
                    f_max = sol2.functions[d]
            
            # Making sure f_max != f_min
            if f_max == f_min :
                min_list.append(0)
                max_list.append(1)

            min_list.append(f_min)
            max_list.append(f_max)

        ranksList = list()
        for p in reference_points :
            ranks = []  # list of solutions ranked based on euclidean distance to p
            for sol in front : 
                ranks.append(normalized_Euclidean_Distance(sol , p , min_list , max_list))
            
            # Adding ranks to ranksList and evaluating other reference points
            ranksList.append([x[1] for x in sorted(zip(ranks , front) , key = lambda x:x[0])])

        # dictionary to sum all ranks for each solution
        d = {sol : 0 for sol in front}
        for rank_p in ranksList : 
            for i in range(len(front)) :
                d[rank_p[i]] += i + 1

        # Returning sorted front

        return sorted(front , key = lambda sol : d[sol])
    else : 
        return front
        



#+----------------------------------------------------------------------------------------------+#


def updateSolutions(solutionsList , fronts , method , reference_points = None) :
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
            selection = crowdingSort(fronts[i])[0:N - len(S)]
            S += selection

        elif method == "referencePoints" : 
            selection = referencePoints(fronts[i] , reference_points)[0:N - len(S)]
            S += selection

    try : 
        for sol in S :
            sol.fitness = fit(sol,solutionsList)
            if sol in solutionsList : 
                sol.limit += 1
    except : 
        None
        
    return S