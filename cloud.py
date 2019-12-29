import numpy
import math
import random
import copy


# product of given list elements

def prod(List):
    result = 1
    for i in List:
        result *= i
    return result


#### class product ####

class Product:

    # constructor

    def __init__(self, unitNumber, unitPrice):
        if isinstance(unitNumber, (int, float)):
            self.__unitNumber = unitNumber
        else:
            raise Exception("unitNumber must be of type : int or float ")
        if isinstance(unitNumber, (int, float)):
            self.__unitPrice = unitPrice
        else:
            raise Exception("unitPrice must be of type : int or float ")

    # price of a product 

    def getPrice(self):
        return self.__unitPrice * self.__unitNumber

    #### class Service ####


class Service:

    # constructor  

    def __init__(self, activity, responseTime, reliability, availability, productList, matching=1):

        if isinstance(activity, (int)):
            self.__activity = activity
        else:
            raise Exception("responseTime must be of type : int or float ")

        if isinstance(responseTime, (int, float)):
            self.__responseTime = responseTime
        else:
            raise Exception("responseTime must be of type : int or float ")

        if isinstance(reliability, (int, float)):
            self.__reliability = reliability
        else:
            raise Exception("reliability must be of type : int or float ")

        if isinstance(availability, (int, float)):
            self.__availability = availability
        else:
            raise Exception("availability must be of type : int or float ")

        if isinstance(productList, (list, tuple)):
            self.__price = sum([p.getPrice() for p in productList])
        else:
            raise Exception("productsList must be of type : list or tuple ")

        if isinstance(matching, (int, float)) and 0 < matching <= 1:
            self.__matching = matching
        else:
            raise Exception("matching must be between 0 and 1")

    # get attributs

    def getResponseTime(self):
        return self.__responseTime

    def getPrice(self):
        return self.__price

    def getReliability(self):
        return self.__reliability

    def getAvailability(self):
        return self.__availability

    def getMatching(self):
        return self.__matching

    def getActivity(self):
        return self.__activity

    #  Euclidean Distance

    def euclideanDist(self, service):

        dRes = self.__responseTime - service.getResponseTime()
        dPri = self.__price - service.getPrice()
        dRel = self.__reliability - service.getReliability()
        dAva = self.__availability - service.getAvailability()

        return math.sqrt(dRes ** 2 + dPri ** 2 + dRel ** 2 + dAva ** 2)

    ##### class workflow #####


class CompositionPlan:
    # a fin de calculer le QOS de chaque Plan de composition
    # constructor

    # argument serviceArcs is a list of lists each list represents an arc [S1 , S2 , 0 or 1 or -1]

    def __init__(self, rootservice, serviceArcs):
        self.rootservice = rootservice
        self.graph = {}  # Dicitonary : source service is a key ,list of destination services and type are values
        self.servSet = set()  # set of services present in the Graph
        for i in serviceArcs:
            self.servSet.add(i[0])
            self.servSet.add(i[1])
            if i[0] not in self.graph.keys():  # creating non-exisitent key
                self.graph[i[0]] = [[i[1], i[2]]]
            else:
                self.graph[i[0]].append([i[1], i[2]])  # Appending existent value with a new destination

    # Calcul Methods

    def evaluateResponseTime(self, rootservice=None):
        if rootservice == None:
            rootservice = self.rootservice
        graph = self.graph
        if rootservice not in graph.keys():  # node with no destination
            return rootservice.getResponseTime()
        else:
            outgoing = graph[rootservice]  # outgoing arcs
            arc = outgoing[0]  # first arc
            # dest = arc[0]
            # type = arc[1]
            if arc[1] == 0:
                # type = sequential
                return rootservice.getResponseTime() + self.evaluateResponseTime(arc[0])
            elif arc[1] == -1:
                # type = conditional
                s = 0
                n = 0
                for arc in outgoing:
                    n += 1
                    s += self.evaluateResponseTime(arc[0])
                return (s / n) + rootservice.getResponseTime()
            elif arc[1] == 1:
                # type = parallel
                return rootservice.getResponseTime() + max([self.evaluateResponseTime(arc[0]) for arc in outgoing])

    def evaluatePrice(self, rootservice=None):
        if rootservice == None:
            rootservice = self.rootservice
        graph = self.graph
        if rootservice not in graph.keys():  # node with no destination
            return rootservice.getPrice()
        else:
            outgoing = graph[rootservice]  # outgoing arcs
            arc = outgoing[0]  # first arc
            # dest = arc[0]
            # type = arc[1]
            if arc[1] == 0:
                # type = sequential
                return rootservice.getPrice() + self.evaluatePrice(arc[0])

            elif arc[1] == -1:
                # type = conditional
                s = 0
                n = 0
                for arc in outgoing:
                    n += 1
                    s += self.evaluatePrice(arc[0])
                return (s / n) + rootservice.getPrice()
            elif arc[1] == 1:
                # type = parallel
                return rootservice.getPrice() + sum([self.evaluatePrice(arc[0]) for arc in outgoing])

    def evaluateAvailability(self, rootservice=None):
        if rootservice == None:
            rootservice = self.rootservice
        graph = self.graph
        if rootservice not in graph.keys():  # node with no destination
            return rootservice.getAvailability()
        else:
            outgoing = graph[rootservice]  # outgoing arcs
            arc = outgoing[0]  # first arc
            # dest = arc[0]
            # type = arc[1]
            if arc[1] == 0:
                # type = sequential
                return rootservice.getAvailability() * self.evaluateAvailability(arc[0])
            elif arc[1] == -1:
                # type = conditional
                s = 0
                n = 0
                for arc in outgoing:
                    n += 1
                    s += self.evaluateAvailability(arc[0])
                return (s / n) * rootservice.getAvailability()
            elif arc[1] == 1:
                # type = parallel
                return rootservice.getAvailability() * prod([self.evaluateAvailability(arc[0]) for arc in outgoing])

    def evaluateReliability(self, rootservice=None):
        if rootservice == None:
            rootservice = self.rootservice
        graph = self.graph
        if rootservice not in graph.keys():  # node with no destination
            return rootservice.getReliability()
        else:
            outgoing = graph[rootservice]  # outgoing arcs
            arc = outgoing[0]  # first arc
            # dest = arc[0]
            # type = arc[1]
            if arc[1] == 0:
                # type = sequential
                return rootservice.getReliability() * self.evaluateReliability(arc[0])
            elif arc[1] == -1:
                # type = conditional
                s = 0
                n = 0
                for arc in outgoing:
                    n += 1
                    s += self.evaluateReliability(arc[0])
                return (s / n) * rootservice.getReliability()
            elif arc[1] == 1:
                # type = parallel
                return rootservice.getReliability() * prod([self.evaluateReliability(arc[0]) for arc in outgoing])

    # Quality of Service

    def QoS(self, qosMin, qosMax,weightList=[1, 1, 1, 1]):  # weightList should be in order (Price,ResponseTime,Availability,Reliability)
        rt = (qosMax['responseTime'] - self.evaluateResponseTime()) / (qosMax['responseTime'] - qosMin['responseTime'])
        pr = (qosMax['price'] - self.evaluatePrice()) / (qosMax['price'] - qosMin['price'] +1)
        av = (self.evaluateAvailability() - qosMin['availability']) / (qosMax['availability'] - qosMin['availability'])
        rel = (self.evaluateReliability() - qosMin['reliability']) / (qosMax['reliability'] - qosMin['reliability'])
        vect1 = numpy.array([rt, pr, av, rel])
        # weights
        vect2 = numpy.array(weightList)
        # vectorial product
        return numpy.dot(vect1, vect2)

    # Matching degree
    def evaluateMatching(self, rootservice=None):
        if rootservice == None:
            rootservice = self.rootservice
        graph = self.graph
        servNumber = len(self.servSet)
        if rootservice not in graph.keys():  # node with no destination
            return rootservice.getMatching() / servNumber
        else:
            outgoing = graph[rootservice]  # list of arcs linked to rootservice
            s = 0
            for arc in outgoing:
                s += self.evaluateMatching(arc[0])
            return s + (rootservice.getMatching() / servNumber)

    # Modifying workflow by mutating a service

    def mutate(self, target, new):
        if target.getActivity() == new.getActivity():  # Activity matching true
            self.servSet.remove(target)  # Updating servSet
            self.servSet.add(new)
            if self.rootservice == target:
                self.graph[new] = self.graph.pop(self.rootservice)
                self.rootservice = target  # if target is rootservice than update attribut
            else:
                for service in self.graph.keys():
                    if service == target:
                        self.graph[new] = self.graph.pop(
                            service)  # replacing old service with new and keeping outgoing arcs

                    else:
                        for arc in self.graph[service]:
                            if arc[0] == target:  # replacing old service if found in other arcs
                                arc[0] = new
                                break
        else:
            raise Exception("Activity mismatch !")

    # choose randomly return a service
    def randomServ(self):
        return random.sample(self.servSet, 1)[0]


# Random workflow generating function

def randomCompositionPlan(rootAct, actGraph, services):
    # actGraph : Activity graph is like serviceArcs but S1 and S2 are replaced with activities indexes
    # this function generates random services to fill the serviceArcs
    serviceArcs = copy.deepcopy(actGraph)
    for act in range(1, len(services) + 1):
        # random service for activity act
        s = random.sample(services[act - 1], 1)[0]
        if act == rootAct:
            rootservice = s
        for arc in serviceArcs:
            # changing activity by service
            if arc[0] == act:
                arc[0] = s
            elif arc[1] == act:
                arc[1] = s
    w = CompositionPlan(rootservice, serviceArcs)
    return (w)


# Modifying workflow by workflow-CROSSOVER 

def crossover(w1, w2):  # w1 and w2 two parents
    # child is a copy of w1
    serviceArcs = []
    for i in w1.graph.keys():
        arc = [i]
        for dest in w1.graph[i]:
            arc.extend(dest)
            serviceArcs.append(arc)

    child = CompositionPlan(w1.rootservice, serviceArcs)

    for serv in w2.servSet:  # Selecting services from 2nd workflow (parameter)
        if random.randint(0, 1):  # 50 % chance of mutation
            for target in child.servSet:
                if target.getActivity() == serv.getActivity():  # Searching for matching targets
                    child.mutate(target, serv)  # Mutate

    return (child)
