import cloud
from numpy import array , dot
from random import random , randint , sample
from math import inf

# SQ : condition for scouts , MCN : number of iterations
def ABCgenetic(actGraph, candidates, SQ, MCN,constraints, weightList):

    ############################# operations definition ##################################

    # returning the nearest neighbor of service based on euclidean distance
    def getNeighbor(service):
        neighborsList = candidates[service.getActivity()]
        return min([neighbor for neighbor in neighborsList if neighbor != service], key=lambda x: service.euclideanDist(x))

    def updateBest(fit = None) :
        nonlocal best_fit , best_cp
        if fit == None :        # No parameters passed
            fit = max(fitnessList)

        if  fit > best_fit :
            best_fit = fit      # Updating best fitness
            pos = fitnessList.index(fit)
            best_cp = solutionsList[pos]   # Updating best solution
            best_Qos = QosList[pos]

    def verifyConstraints(QosDict) :
        drt = constraints['responseTime'] - QosDict['responseTime']
        dpr = constraints['price'] - QosDict['price']
        dav = QosDict['availability'] - constraints['availability']
        drel = QosDict['reliability'] - constraints['reliability']

        return drt and dpr and dav and drel

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
        for QosDict in QosList :
            for qos in QosDict :
                if QosDict[qos] < minQos[qos] :
                    minQos[qos] = QosDict[qos]
                if QosDict[qos] > maxQos[qos] :
                    maxQos[qos] = QosDict[qos]
        # Updating best fitness
        try :
            _ , best_fit = f(best_cp)
        except : # best_cp not created
            None
        # updating fitnessList
        for i in range(SN) :
            _ , fitnessList[i] = f(solutionsList[i])




    # Objective function
    def f(cp):
        QosDict = cp.cpQos()
        if verifyConstraints(QosDict) :
            rt = (maxQos['responseTime'] - QosDict['responseTime']) / (maxQos['responseTime'] - minQos['responseTime'])
            pr = (maxQos['price'] - QosDict['price']) / (maxQos['price'] - minQos['price'])
            av = (QosDict['availability'] - minQos['availability']) / (maxQos['availability'] - minQos['availability'])
            rel = (QosDict['reliability'] - minQos['reliability']) / (maxQos['reliability'] - minQos['reliability'])

            vect1 = array([rt, pr, av, rel])
            # weights
            vect2 = array(weightList)
            # vectorial product
            globalQos =  dot(vect1, vect2)
            return QosDict , globalQos + cp.cpMatching()

        else :  # constraints not verified
            return -1

    # Mutation
    def mutate(cp, new):
        # new is added to the composition plan
        cp.G.nodes[new.getActivity()]["service"] = new


    # Crossover
    def crossover(parent1, parent2):
        # creating new child identical to first parent
        actGraph = list(parent1.G.edges.data("weight"))  # getting actGraph from parent
        parent1_services = [[act[1]] for act in list(parent1.G.nodes.data("service"))] # getting services from parent
        child = cloud.CompositionPlan(actGraph, parent1_services)

        # modifying child
        for act in child.G.nodes:  # Selecting service to replace
            if randint(0, 1):  # 50 % chance of crossover
                # replacing with service from second parent
                child.G.nodes[act]["service"] = parent2.G.nodes[act]["service"]

        return child



    ############################# Algorithm start  ##################################

    # initializing parameters

    SN = 20           # SN : number of ressources
    SCP = 4 * MCN / 5  # changing point for scouts


    # solutions , fitness , maxQos and minQos initializing
    solutionsList = list()
    fitnessList = list(0 for i in range(SN))
    QosList = list()
    minQos = {'responseTime': inf,'price' : inf,'availability' : inf,'reliability' : inf}
    maxQos = {'responseTime': 0,'price' : 0,'availability' : 0,'reliability' : 0}
    probabilityList = list(0 for i in range(SN))
    limit = list(0 for i in range(SN))

    for i in range(SN):
        while 1:
            cp = cloud.CompositionPlan(actGraph, candidates)
            QosDict = cp.cpQos()

            if verifyConstraints(QosDict) :
                solutionsList.append(cp)
                QosList.append(QosDict)
                break


    # initializing best_fit and best_cp
    updateMinMax()
    best_fit = max(fitnessList)
    pos = fitnessList.index(best_fit)
    best_cp =  solutionsList[pos]
    best_Qos = QosList[pos]
    # Algorithm
    for itera in range(MCN):
        # employed bees phase
        exploited = sample(list(range(SN)),SN // 2)   # Generating positions list for exploitation
        for i in exploited :
            cp1 = solutionsList[i]
            cp2 = cloud.CompositionPlan(actGraph, candidates) # randomly generated cp
            child = crossover(cp1, cp2) # Crossover operation
            child_Qos , fit = f(child)
            if fit > fitnessList[i]:  # checking if child fitness is better than parent fitness
                fitnessList[i] = fit
                solutionsList[i] = child
                QosList[i] = child_Qos
                limit[i] = 0
            else:
                limit[i] += 1
        # end of employed bees phase

        updateBest()

        # Probability update
        for i in exploited :
            s = sum(fitnessList)
            probabilityList[i] = fitnessList[i] / s

        # onlooker bees phase
        for i in exploited:
            if probabilityList[i] > random():
                cp1 = solutionsList[i]
                cp2 = best_cp   # current best
                child = crossover(cp1, cp2) # Crossover operation
                child_Qos , fit = f(child)
                if fit > fitnessList[i]:    # checking if child fitness is better than parent fitness
                    fitnessList[i] = fit
                    solutionsList[i] = child
                    QosList[i] = child_Qos
                    limit[i] = 0
                    updateBest(fit)
                else:
                    limit[i] += 1
        # end of onlooker bees phase

        # scout bees phase
        for i in exploited:
            if limit[i] == SQ:  # verifying scouts condition
                if itera >= SCP: # change of scouts behaviour condition to mutating
                    cp = solutionsList[i]
                    while 1:
                        # choose randomly a service to mutate
                        service = cp.G.nodes[randint(0, cp.G.number_of_nodes() - 1)]["service"]
                        neighbor = getNeighbor(service)
                        # mutation operation
                        mutate(cp,neighbor)
                        QosDict ,fit = f(cp)

                        if fit:   # verifying constraints compatibility of mutated ressource
                            solutionsList[i] = cp
                            fitnessList[i] = fit
                            QosList[i] = QosDict
                            break

                else:   # searching for new ressources to exploit
                    while 1:
                        cp = cloud.CompositionPlan(actGraph, candidates)
                        QosDict , fit = f(cp)
                        if fit:  # verifying constraints compatibility of new ressource
                            solutionsList[i] = cp
                            fitnessList[i] = fit
                            QosList[i] = QosDict
                            break

                limit[i] = 0
        # end of scout bees phase
        updateMinMax()

    # end of algorithm
    return best_cp , best_fit
