from numpy import array
from random import uniform , randint , sample
from prettytable import PrettyTable

from data_structure.Composition_plan import CompositionPlan


def verifyConstraints(QosDict,constraints) :
    drt = constraints['responseTime'] - QosDict['responseTime']
    dpr = constraints['price'] - QosDict['price']
    dav = QosDict['availability'] - constraints['availability']
    drel = QosDict['reliability'] - constraints['reliability']

    return drt and dpr and dav and drel


def functions(cp) :
    QosDict = cp.cpQos()
    f1 = - QosDict["responseTime"]
    f2 = - QosDict["price"]
    f3 = QosDict["availability"] + QosDict["reliability"]
    return array([f1,f2,f3])



# SQ : condition for scouts , MCN : number of iterations
def moabc_nsga2(actGraph, candidates, SQ, MCN,constraints):

    ############################# operations definition ##################################
    print("SN = 10 , SQ = 2 , MCN = 10")

    def show_solutions(X) :
        t = PrettyTable(['solution','fitness',"f1","f2","f3",'probability','limit'])
        for i in range(len(X)) :
            t.add_row([i, X[i]["fitness"],X[i]["functions"][0],X[i]["functions"][1],X[i]["functions"][2] , X[i]["probability"],X[i]["limit"]])
        print(t)

    def show_solution(cp) :
        t = PrettyTable(['fitness',"f1","f2","f3",'probability','limit'])
        t.add_row([cp["fitness"],cp["functions"][0],cp["functions"][1],cp["functions"][2] , cp["probability"],cp["limit"]])
        print(t)
        print("services are :")
        show_services(cp["cp"])

    def show_services(cp) :
        t = PrettyTable(['activity', 'price','responseTime','availability','reliability','matching'])
        for i in range(cp.G.number_of_nodes()) :
            t.add_row([i, cp.G.nodes[i]["service"].getPrice(),cp.G.nodes[i]["service"].getResponseTime() , cp.G.nodes[i]["service"].getAvailability(),cp.G.nodes[i]["service"].getReliability(),cp.G.nodes[i]["service"].getMatching()])
        print(t)

    def show_neighbors() :
        t = PrettyTable(['solution','fitness',"f1","f2","f3",'probability','limit'])
        for i in range(4) :
            t.add_row([i, neighbors[i]["fitness"],neighbors[i]["functions"][0],neighbors[i]["functions"][1],neighbors[i]["functions"][2] , neighbors[i]["probability"],neighbors[i]["limit"]])
        print(t)

    def show_fronts() :
        for i in range(len(fronts)-1) :
            print(f"front {i} : ")
            t = PrettyTable(['solution','f1','f2','f3'])
            for j in range(len(fronts[i])) :
                t.add_row([j,fronts[i][j]["functions"][0],fronts[i][j]["functions"][1],fronts[i][j]["functions"][2]])
            print(t)


    def fit(cp):
        dom = 1
        F = functions(cp)
        for i in range(SN) :
            G = functions(solutionsList[i]["cp"])
            if (F >= G).all() and (F > G).any() :
                dom += 1
        return dom / SN

    def BSG(cp1, cp2 , constraints):

        # Crossover

        # First neighbor

        neighbor1 = cp1.clone()

        while 1 :
            x1 = randint(0,cp2.G.number_of_nodes()-2)
            x2 = randint(x1+1,cp2.G.number_of_nodes()-1)
            for act in range(x1,x2+1):  # Selecting service to replace
                    # replacing with service from second parent
                    neighbor1.G.nodes[act]["service"] = cp2.G.nodes[act]["service"]
            if verifyConstraints(neighbor1.cpQos() , constraints) :
                break

        print(f"BSG 1 : x1 = {x1} , x2 = {x2}")

        # Second neighbor

        neighbor2 = cp2.clone()

        while 1 :
            x1 = randint(0,cp1.G.number_of_nodes()-2)
            x2 = randint(x1+1,cp1.G.number_of_nodes()-1)
            for act in range(x1,x2+1):  # Selecting service to replace
                    # replacing with service from second parent
                    neighbor2.G.nodes[act]["service"] = cp1.G.nodes[act]["service"]
            if verifyConstraints(neighbor2.cpQos() , constraints) :
                break

        print(f"BSG 2 : x1 = {x1} , x2 = {x2}")


        # Mutation

        # First neighbor

        neighbor3 = cp1.clone()

        # choose randomly a service to mutate
        service = neighbor3.G.nodes[randint(0, neighbor3.G.number_of_nodes() - 1)]["service"]
        while 1 :
            new = sample(candidates[service.getActivity()],1)[0]
            # mutation operation
            neighbor3.G.nodes[new.getActivity()]["service"] = new
            if verifyConstraints(neighbor3.cpQos() , constraints) :
                break

        print(f"BSG 3 : x1 = {x1} , x2 = {x2}")
        # Second neighbor

        neighbor4 = cp2.clone()

        # choose randomly a service to mutate
        service = neighbor4.G.nodes[randint(0, neighbor4.G.number_of_nodes() - 1)]["service"]
        while 1 :
            new = sample(candidates[service.getActivity()],1)[0]
            # mutation operation
            neighbor4.G.nodes[new.getActivity()]["service"] = new
            if verifyConstraints(neighbor4.cpQos() , constraints) :
                break

        print(f"BSG 4 : x1 = {x1} , x2 = {x2}")

        neighborsList = [neighbor1 , neighbor2 , neighbor3 , neighbor4]
        return [{"cp" : cp , "fitness" : 0 , "functions" : functions(cp) , "limit" : 0 , "probability" : 0} for cp in neighborsList]



    def nonDominatedSort(X) :
        fronts = [[]]
        SList = list()
        NList = list()
        for p in range(len(X)) :
            Sp = list()
            Np = 0
            F = X[p]["functions"]
            for q in range(len(X)) :
                G = X[q]["functions"]
                if q != p and (F >= G).all() and (F > G).any() :
                    Sp.append(q)
                elif q != p and (G >= F).all() and (G > F).any() :
                    Np += 1
            NList.append(Np)
            if Np == 0 :
                fronts[0].append(p)
            SList.append(Sp)

        i = 0
        while len(fronts[i]) != 0 :
            f = []
            for p in fronts[i] :
                for q in SList[p] :
                    NList[q] -= 1
                    if NList[q] == 0 :
                        f.append(q)
            i += 1
            fronts.append(f)

        return [[X[p] for p in f] for f in fronts]


    def crowdingSort(front) :
        scoresList = list()
        for p in front :
            score = list()
            for f in range(3) :
                high = []
                low = []
                for q in front :
                    if q["functions"][f] < p["functions"][f]  :
                        low.append(q["functions"][f])
                    if q["functions"][f] > p["functions"][f] :
                        high.append(q["functions"][f])
                if len(high) == 0 :
                    next_high = p["functions"][f]
                else :
                    next_high = min(high)
                if len(low) == 0 :
                     next_low = p["functions"][f]
                else :
                    next_low = max(low)
                score.append(next_high-next_low)
            scoresList.append(sum(score))

        L = [i[1] for i in sorted(zip(scoresList , front) , key = lambda x:x[0] , reverse = True)]
        print("Crowding scores are :")
        t = PrettyTable(['solution','score'])
        for i in range(len(scoresList)) :
            t.add_row([i, scoresList[i]])
        print(t)
        return L


    def updateSolutions(solutionsList , fronts) :
        i = 0
        S = []

        while i < len(fronts) and len(fronts[i]) <= SN - len(S) :
            S += fronts[i]
            i += 1

        if i < len(fronts) :
            crowding_selection = crowdingSort(fronts[i])[0:SN - len(S)]
            S += crowding_selection

        for cp in S :
            if cp in solutionsList :
                cp["limit"] += 1

        solutionsList[:] = S

        for cp in solutionsList :
            cp["fitness"] = fit(cp["cp"])







    ############################# Algorithm start  ##################################

    # initializing parameters

    SN = 10           # SN : number of ressources

    # solutions  initializing
    solutionsList = list()

    for i in range(SN):
        while 1:
            cp = CompositionPlan(actGraph, candidates)
            QosDict = cp.cpQos()
            if verifyConstraints(QosDict,constraints) :
                solutionsList.append({"cp" : cp , "fitness" : 0 , "functions" : functions(cp) , "limit" : 0 , "probability" : 0})
                break



    show_solutions(solutionsList)
    print("algorithm start")
    # Algorithm
    for itera in range(MCN):

        # employed bees phase
        print("employed bees phase ...")
        exploited = sample(list(range(SN)),SN // 2)   # Generating positions list for exploitation
        print(f"exploited solutions = {exploited}")
        U = list()
        U[:] = solutionsList
        for i in exploited :
            print(f"solution {i} chosen ... ")
            cp1 = solutionsList[i]["cp"]
            show_solution(solutionsList[i])
            cp2 = CompositionPlan(actGraph, candidates) # randomly generated cp
            print("randomly generating a composition plan")
            print(show_solution({"cp" : cp2 , "fitness" : 0 , "functions" : functions(cp2) , "limit" : 0 , "probability" : 0}))
            neighbors = BSG(cp1, cp2 , constraints) # BSG
            print("generating neighbors by BSG ...")
            show_neighbors()
            U += neighbors

        print("solutionsList after adding neighbors !")
        show_solutions(U)
        print("end of employed bees phase")
        # end of employed bees phase
        print("Appplying nonDominatedSort and updating solutionsList")
        fronts = nonDominatedSort(U)
        print("Fronts calculated !")
        show_fronts()
        updateSolutions(solutionsList , fronts)
        show_solutions(solutionsList)
        # Probability update
        s = sum([solutionsList[i]["fitness"] for i in range(SN)])
        for i in exploited :
            solutionsList[i]["probability"] = solutionsList[i]["fitness"] / s
        print("probability calculated !")

        show_solutions(solutionsList)
        # onlooker bees phase
        print("onlooker bees phase ...")
        U = list()
        U[:] = solutionsList
        for i in exploited :
            print(f"solution {i} chosen ... ")
            r = uniform(min([solutionsList[x]["probability"] for x in range(SN)]) , max([solutionsList[x]["probability"] for x in range(SN)]))
            print(f"probability = {solutionsList[i]['probability']} vs random = {r}")

            if solutionsList[i]["probability"] > r :
                cp1 = solutionsList[i]["cp"]
                show_solution(solutionsList[i])
                cp2 = CompositionPlan(actGraph, candidates) # randomly generated cp
                print("randomly generating a composition plan")
                show_solution({"cp" : cp2 , "fitness" : 0 , "functions" : functions(cp2) , "limit" : 0 , "probability" : 0})
                neighbors = BSG(cp1, cp2 , constraints) # BSG
                U += neighbors
                show_neighbors()

        print("solutionsList after adding neighbors !")
        show_solutions(U)
        print("end of onlooker bees phase")
        # end of onlooker bees phase
        print("Appplying nonDominatedSort and updating solutionsList")
        fronts = nonDominatedSort(U)
        print("Fronts calculated !")
        show_fronts()
        updateSolutions(solutionsList , fronts)
        show_solutions(solutionsList)
        # scout bees phase
        print("Scout bees phase ...")
        update = 0
        U = list()
        U[:] = solutionsList
        for i in exploited :
            if solutionsList[i]["limit"] >= SQ :
                print(f"solution {i} reached limit ... ")
                while 1 :
                    cp = CompositionPlan(actGraph, candidates) # randomly generated cp
                    if verifyConstraints(cp.cpQos(),constraints) :
                        new_solution = {"cp" : cp , "fitness" : fit(cp) , "functions" : functions(cp) , "limit" : 0 , "probability" : 0}
                        U += [new_solution]
                        print("generating new solution ...")
                        show_solution(new_solution)
                        break
                print("randomly generating a composition plan")
                show_solution({"cp" : cp , "fitness" : 0 , "functions" : functions(cp) , "limit" : 0 , "probability" : 0})
                update = 1
        print("end of scout bees phase ...")
        # end of scout bees phase
        if update :
            print("solutionsList after adding new scout solutions !")
            show_solutions(U)
            print("Appplying nonDominatedSort and updating solutionsList")
            fronts = nonDominatedSort(U)
            print("Fronts calculated !")
            show_fronts()
            updateSolutions(solutionsList , fronts)
            show_solutions(solutionsList)

    # end of algorithm
    print("\n")
    for sol in solutionsList :
        print(f"possible solution :\n{sol['cp'].cpQos()}\n")
