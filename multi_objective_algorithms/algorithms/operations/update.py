
from multi_objective_algorithms.algorithms.operations.objective_functions import functions , fit , dominates
from random import sample
from numpy import amin , amax , array 

#+----------------------------------------------------------------------------------------------+#

# transform Solutions list into numpy matrix
def transform(U) :
    return array([x.functions for x in U])

#+----------------------------------------------------------------------------------------------+#


# return max_pf - min_pf euclidean distance
def normalize(pf) :
    return euclidean_Distance(amax(pf , axis = 0) , amin(pf , axis = 0))

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


def normalized_Euclidean_Distance(a , b , norm) :
    return euclidean_Distance(a,b) / norm


#+----------------------------------------------------------------------------------------------+#


def euclidean_Distance(a , b) :
    try : # a , b are numpy array type
        return (( (a - b) ** 2).sum(axis = 0) ** 0.5 )
    except :
        try : # a , b are Solution type
            return (( (a.functions - b.functions) ** 2).sum(axis = 0) ** 0.5 )
        except : # a is Solution type and b is numpy array
            return (( (a.functions - b) ** 2).sum(axis = 0) ** 0.5 )



#+----------------------------------------------------------------------------------------------+#


def referencePoints(front , reference_points , epsilon) :
    if len(front) > 1 :
        norm = normalize(transform(front))
        # verifying that norm != 0
        if norm == 0 :
            norm = 1

        groups = list()
        for p in reference_points :
            ranks = []  # list of solutions ranked based on euclidean distance to p
            for sol in front : 
                ranks.append(normalized_Euclidean_Distance(sol , p , norm))
            
            # Adding ranks to ranksList and evaluating other reference points
            groups.append([x[1] for x in sorted(zip(ranks , front) , key = lambda x:x[0])])

        # Random order of groups 
        n_points = len(reference_points)
        groups = sample(groups , len(reference_points))

        # Re arranging groups in a way to verify epsilon condition
        new_groups = []
        neighbors = []
        for g in groups :
            new_g = [g.pop(0)] 
            for sol1 in new_g :
                for sol2 in g :
                    d = normalized_Euclidean_Distance(sol1 , sol2 , norm)
                    if d <= epsilon :
                        # Adding sol2 to new_g and removing it from g
                        new_g.append(sol2)
                        g.remove(sol2)

            # saving neighbor points in neighbors
            neighbors.extend(new_g[:])

            # Adding the non selected solutions to the end of the group
            new_g += g

            # Adding new group to group list
            new_groups.append(new_g)


        new_front = []

        # starting to fill the new sorted front
        i = 0
        while len(new_front) < len(front) :
            try :
                sol1 = new_groups[i % n_points].pop(0)
                if sol1 not in new_front :
                    new_front.append(sol1)
            except : # No more solutions in this group
                pass
            i += 1

        return new_front , neighbors
 
    else : 
        return front , None
        



#+----------------------------------------------------------------------------------------------+#


def updateSolutions(solutionsList , fronts , method , **kwargs) :
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
            reference_points = kwargs["reference_points"]
            epsilon = kwargs["epsilon"]
            selection = referencePoints(fronts[i] , reference_points , epsilon)[0][0:N - len(S)]
            S += selection

    try : 
        for sol in S :
            sol.fitness = fit(sol,solutionsList)
            if sol in solutionsList : 
                sol.limit += 1
    except : 
        None
        
    return S