import cloud
from numpy import array , dot
from random import uniform , randint , sample
from math import inf
from prettytable import PrettyTable


# returning the nearest neighbor of service based on euclidean distance
def getNeighbor(service , candidates):
    return min([neighbor for neighbor in candidates if neighbor != service], key=lambda x: service.euclideanDist(x))

def verifyConstraints(qos , constraints) :
    drt = constraints['responseTime'] - qos['responseTime']
    dpr = constraints['price'] - qos['price']
    dav = qos['availability'] - constraints['availability']
    drel = qos['reliability'] - constraints['reliability']

    return drt and dpr and dav and drel

# Objective function
def fit(cp, minQos , maxQos , weights):
    qos = cp.cpQos()
    rt = (maxQos['responseTime'] - qos['responseTime']) / (maxQos['responseTime'] - minQos['responseTime'])
    pr = (maxQos['price'] - qos['price']) / (maxQos['price'] - minQos['price'])
    av = (qos['availability'] - minQos['availability']) / (maxQos['availability'] - minQos['availability'])
    rel = (qos['reliability'] - minQos['reliability']) / (maxQos['reliability'] - minQos['reliability'])
    # vectorial product
    return dot(array([rt, pr, av, rel]), weights) + cp.cpMatching()

# Mutation
def mutate(cp, new_service):
    print("mutation execution !")
    new_cp = cp.clone()
    # new is added to the composition plan
    new_cp.G.nodes[new_service.getActivity()]["service"] = new_service
    print("mutation done !")
    return(new_cp)



# Crossover
def crossover(parent1, parent2):

    print("crossover execution !")
    child = parent1.clone()    # creating new child identical to first parent
    # modifying child
    for act in child.G.nodes:  # Selecting service to replace
        if randint(0, 1):  # 50 % chance of crossover
            # replacing with service from second parent
            child.G.nodes[act]["service"] = parent2.G.nodes[act]["service"]
    print("crossover done !")
    return child

# SQ : condition for scouts , MCN : number of iterations
def ABCgenetic(actGraph, candidates,SQ,MCN,constraints, weights):

    print("SN = 10 , SQ = 2 , MCN = 10")
    def show_solutions() :
        t = PrettyTable(['solution', 'fitness','probability','limit'])
        for i in range(SN) :
            t.add_row([i, fitnessList[i] , probabilityList[i],limit[i]])
        t.add_row(["best_cp", best_fit , "",""])
        print(t)

    def show_solution(cp) :
        t = PrettyTable(['activity', 'price','responseTime','availability','reliability','matching'])
        for i in range(cp.G.number_of_nodes()) :
            t.add_row([i, cp.G.nodes[i]["service"].getPrice(),cp.G.nodes[i]["service"].getResponseTime() , cp.G.nodes[i]["service"].getAvailability(),cp.G.nodes[i]["service"].getReliability(),cp.G.nodes[i]["service"].getMatching()])
        print(t)


    def updateBest(fit = None) :
        nonlocal best_fit , best_cp
        if fit == None :        # No parameters passed
            fit = max(fitnessList)

        if  fit > best_fit :
            best_fit = fit      # Updating best fitness
            best_cp = solutionsList[fitnessList.index(fit)]   # Updating best solution


    def updateMinMax() :
        nonlocal best_fit , fitnessList , minQos , maxQos
        # updating minQos and maxQos
        # looking for minQos and maxQos in best_Qos
        try :
            for qos in best_Qos :
                if best_Qos[qos] < minQos[qos] :
                    minQos[qos] = best_Qos[qos]
                if best_Qos[qos] > maxQos[qos] :
                    maxQos[qos] = best_Qos[qos]
        except : # best_Qos not created
            None
        # looking for minQos and maxQos in solutionsList
        for cp in solutionsList :
            qosDict = cp.cpQos()
            for qos in qosDict :
                if qosDict[qos] < minQos[qos] :
                    minQos[qos] = qosDict[qos]
                if qosDict[qos] > maxQos[qos] :
                    maxQos[qos] = qosDict[qos]
        # Updating best fitness
        try :
            best_fit = fit(best_cp, minQos , maxQos , weights)
        except : # best_cp not created
            None
        # updating fitnessList
        for i in range(SN) :
            fitnessList[i] = fit(solutionsList[i], minQos , maxQos , weights)


    ############################# Algorithm start  ##################################
    print("Initialzing ...")
    # initializing parameters
    SN = 10           # SN : number of ressources
    SCP = 4 * MCN / 5  # changing point for scouts


    # solutions and fitness initializing
    solutionsList = list()
    fitnessList = list(0 for i in range(SN))
    probabilityList = list(0 for i in range(SN))
    minQos = {'responseTime': inf,'price' : inf,'availability' : inf,'reliability' : inf}
    maxQos = {'responseTime': 0,'price' : 0,'availability' : 0,'reliability' : 0}
    limit = list(0 for i in range(SN))

    for i in range(SN):
        while 1:
            cp = cloud.CompositionPlan(actGraph, candidates)
            if verifyConstraints(cp.cpQos(),constraints) :
                solutionsList.append(cp)
                break


    #minQos maxQos and fitnessList initializing
    updateMinMax()

    # initializing best_fit and best_cp
    best_fit = max(fitnessList)
    best_cp =  solutionsList[fitnessList.index(best_fit)]
    show_solutions()
    print("algorithm start")
    print("employed bees phase ...")
    # Algorithm
    for itera in range(MCN):
        print(f"iteration = {itera+1}")
        # employed bees phase
        exploited = sample(list(range(SN)),SN // 2)   # Generating positions list for exploitation
        print(f"exploited solutions = {exploited}")
        for i in exploited :
            print(f"solution {i} chosen ... ")
            cp1 = solutionsList[i]
            show_solution(cp1)
            while 1 :
                cp2 = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
                print("generating random plan")
                show_solution(cp2)
                child = crossover(cp1, cp2) # Crossover operation
                show_solution(child)
                if verifyConstraints(child.cpQos(), constraints):
                    new_fitness = fit(child, minQos , maxQos , weights)
                    print(f"new_fitness = {new_fitness}")
                    print(f"old_fitness = {fitnessList[i]}")
                    if new_fitness > fitnessList[i]:  # checking if child fitness is better than parent fitness
                        fitnessList[i] = new_fitness
                        solutionsList[i] = child
                        limit[i] = 0
                        print("replaced !")
                    else:
                        limit[i] += 1
                        print("not replaced !")
                    break
        # end of employed bees phase

        updateBest()
        print("updating best !")
        print("onlooker bees phase ...")
        # Probability update
        for i in exploited :
            s = sum(fitnessList)
            probabilityList[i] = fitnessList[i] / s
        show_solutions()
        # onlooker bees phase
        for i in exploited:
            print(f"solution {i} chosen ... ")
            r = uniform(min(fitnessList)/s,max(fitnessList)/s)
            print(f"probability = {probabilityList[i]} vs random = {r}")
            if probabilityList[i] > r:
                "selected by probability !"
                cp1 = solutionsList[i]
                show_solution(cp1)
                cp2 = best_cp   # current best
                print("crossover with best_cp")
                show_solution(cp2)
                while 1 :
                    child = crossover(cp1, cp2) # Crossover operation
                    show_solution(child)
                    if verifyConstraints(child.cpQos() , constraints):
                        new_fitness = fit(child ,minQos , maxQos , weights)
                        print(f"new_fitness = {new_fitness}")
                        print(f"old_fitness = {fitnessList[i]}")
                        if new_fitness > fitnessList[i]:    # checking if child fitness is better than parent fitness
                            fitnessList[i] = new_fitness
                            solutionsList[i] = child
                            limit[i] = 0
                            print("replaced !")
                            updateBest(new_fitness)
                            print("updating best !")
                        else:
                            limit[i] += 1
                            print("not replaced !")
                        break
        # end of onlooker bees phase
        print("scouts bees phase ...")
        show_solutions()
        # scout bees phase
        for i in exploited:
            if limit[i] >= SQ:  # verifying scouts condition
                print(f"solution {i} reached limit ... ")
                if itera >= SCP: # change of scouts behaviour condition to mutating
                    cp = solutionsList[i]
                    show_solution(cp)
                    while 1:
                        # choose randomly a service to mutate
                        x = randint(0, cp.G.number_of_nodes() - 1)
                        service = cp.G.nodes[x]["service"]
                        print(f"the service of activity {x} will be mutated")
                        neighborsList = candidates[service.getActivity()]
                        neighbor = getNeighbor(service,neighborsList)
                        # mutation operation
                        new = mutate(cp,neighbor)
                        if verifyConstraints(new.cpQos(), constraints):
                            show_solution(new)
                            solutionsList[i] = new
                            fitnessList[i] = fit(new ,minQos , maxQos , weights)
                            break

                else:   # searching for new ressources to exploit
                    while 1:
                        print("generating random solution instead !")
                        cp = cloud.CompositionPlan(actGraph, candidates)
                        if verifyConstraints(cp.cpQos(), constraints) :
                            solutionsList[i] = cp
                            fitnessList[i] = fit(cp , minQos , maxQos , weights)
                            break

                limit[i] = 0
        # end of scout bees phase
        updateMinMax()
        print("end of iteration")
        show_solutions()

    print("end of algorithm")
    # end of algorithm
    return best_cp
