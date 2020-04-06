from prettytable import PrettyTable
from random import uniform, sample
from data_structure.CompositionPlan import CompositionPlan
from data_structure.Solution import Solution
from genetic_operations.implementation import BSG
from multi_objective_algorithms.algorithms.operations.objective_functions import functions
from multi_objective_algorithms.algorithms.operations.update import updateSolutions, nonDominatedSort


def show_solutions(solutionsList) :
    t = PrettyTable(['solution','fitness',"f1","f2","f3",'probability','limit'])
    for i , sol in enumerate(solutionsList) :
        t.add_row([i, sol.fitness,sol.functions[0],sol.functions[1],sol.functions[2] , sol.probability,sol.limit])
    print(t)

def show_solution(sol) :
    t = PrettyTable(['fitness',"f1","f2","f3",'probability','limit'])
    t.add_row([sol.fitness,sol.functions[0],sol.functions[1],sol.functions[2] , sol.probability,sol.limit])
    print(t)
    print("services are :")
    show_services(sol.cp)

def show_services(cp) :
    t = PrettyTable(['activity', 'price','responseTime','availability','reliability','matching'])
    for i in range(cp.getNumberOfActivities()) :
        t.add_row([i, cp.getService(i).getPrice(),cp.getService(i).getResponseTime() , cp.getService(i).getAvailability(),cp.getService(i).getReliability(),cp.getService(i).getMatching()])
    print(t)

def show_fronts(fronts) :
    for i in range(len(fronts)-1) :
        print(f"front {i} : ")
        t = PrettyTable(['solution','f1','f2','f3'])
        for j , sol in enumerate(fronts[i]) :
            t.add_row([j,sol.functions[0], sol.functions[1], sol.functions[2]] )
        print(t)


# SQ : condition for scouts , MCN : number of iterations
def simMoabc_nsga2(problem, SQ, MCN, SN, N):

    print("SN = 10 , SQ = 2 , MCN = 10")

    # solutions  initializing
    solutionsList = list()

    for i in range(SN):
        while 1:
            cp = CompositionPlan(problem.getActGraph(), problem.getCandidates())
            if cp.verifyConstraints(problem.getConstraints()):
                solutionsList.append(Solution(cp=cp, fitness=0, functions=functions(cp), probability=0, limit=0))
                break



    show_solutions(solutionsList)
    print("algorithm start")
    # Algorithm
    for itera in range(MCN):

        # employed bees phase
        print("employed bees phase ...")
        exploited = sample(list(range(SN)),N)   # Generating positions list for exploitation
        print(f"exploited solutions = {exploited}")
        U = list()
        U[:] = solutionsList
        for i in exploited :
            sol = solutionsList[i]
            print(f"solution {i} chosen ... ")
            show_solution(sol)
            cp1 = sol.cp
            cp2 = CompositionPlan(problem.getActGraph(), problem.getCandidates())  # randomly generated cp
            print("randomly generating a composition plan")
            show_solution(Solution(cp = cp2 , fitness =  0 , functions =  functions(cp2) , limit =  0 , probability =  0))
            print("generating neighbors by BSG ...")
            offsprings = BSG(cp1, cp2, problem.getConstraints(), problem.getCandidates())  # BSG
            U += [Solution(cp = cp , fitness = 0 , functions = functions(cp) , probability = 0 , limit = 0) for cp in offsprings]
            show_solutions([Solution(cp = cp , fitness = 0 , functions = functions(cp) , probability = 0 , limit = 0) for cp in offsprings])

        print("solutionsList after adding neighbors !")
        show_solutions(U)
        print("end of employed bees phase")
        # end of employed bees phase
        print("Appplying nonDominatedSort and updating solutionsList")
        fronts = nonDominatedSort(U)
        print("Fronts calculated !")
        show_fronts(fronts)
        updateSolutions(solutionsList, fronts, method="crowdingSort")
        show_solutions(solutionsList)
        

        # Probability update
        s = sum([sol.fitness for sol in solutionsList])
        for i in exploited:
            sol = solutionsList[i]
            sol.probability = sol.fitness / s

        print("probability calculated !")

        show_solutions(solutionsList)
        # onlooker bees phase
        print("onlooker bees phase ...")
        probabilityList = [sol.probability for sol in solutionsList]
        a = min(probabilityList)
        b = max(probabilityList)
        U = list()
        U[:] = solutionsList
        for i in exploited :
            sol = solutionsList[i]
            print(f"solution {i} chosen ... ")
            r = uniform(a , b)
            print(f"probability = {sol.probability} vs random = {r}")
            if sol.probability >= r :
                cp1 = sol.cp
                cp2 = CompositionPlan(problem.getActGraph(), problem.getCandidates())  # randomly generated cp
                print("randomly generating a composition plan")
                show_solution(Solution(cp = cp2 , fitness =  0 , functions =  functions(cp2) , limit =  0 , probability =  0))
                print("generating neighbors by BSG ...")
                offsprings = BSG(cp1, cp2, problem.getConstraints(), problem.getCandidates())  # BSG
                U += [Solution(cp = cp , fitness = 0 , functions = functions(cp) , probability = 0 , limit = 0) for cp in offsprings]
                show_solutions([Solution(cp = cp , fitness = 0 , functions = functions(cp) , probability = 0 , limit = 0) for cp in offsprings])

        print("solutionsList after adding neighbors !")
        show_solutions(U)
        print("end of onlooker bees phase")
        # end of onlooker bees phase
        print("Appplying nonDominatedSort and updating solutionsList")
        fronts = nonDominatedSort(U)
        print("Fronts calculated !")
        show_fronts(fronts)
        updateSolutions(solutionsList, fronts, "crowdingSort")
        show_solutions(solutionsList)

        # scout bees phase
        print("Scout bees phase ...")
        update = 0
        U = list()
        U[:] = solutionsList
        for i in exploited :
            sol = solutionsList[i]
            if sol.limit >= SQ :
                sol.limit = 0
                print(f"solution {i} reached limit ... ")
                while 1 :
                    cp = CompositionPlan(problem.getActGraph(), problem.getCandidates()) # randomly generated cp
                    if cp.verifyConstraints(problem.getConstraints()) :
                        print("randomly generating a composition plan")
                        print("generating new solution ...")
                        new_solution = Solution(cp = cp , fitness = 0 , functions = functions(cp) , probability = 0 , limit = 0)
                        U.append(new_solution)
                        show_solution(new_solution)
                        break
                update = 1
        print("end of scout bees phase ...")
        # end of scout bees phase
        if update :
            print("solutionsList after adding new scout solutions !")
            show_solutions(U)
            print("Appplying nonDominatedSort and updating solutionsList")
            fronts = nonDominatedSort(U)
            print("Fronts calculated !")
            show_fronts(fronts)
            updateSolutions(solutionsList, fronts, "crowdingSort")
            show_solutions(solutionsList)

    # end of algorithm
    print("\n")
    for sol in solutionsList :
        print(f"possible solution :\n{sol.cp.cpQos()}\n")
