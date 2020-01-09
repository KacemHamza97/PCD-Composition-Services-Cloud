import numpy
import math
import networkx as nx
import random
import copy
from functools import reduce


# product of given list elements

def prod(List):
    return reduce((lambda x, y: x * y), List)
    #### class Service ####


class Service:

    # constructor

    def __init__(self, activity, responseTime, reliability, availability, price, matching=1):

        if isinstance(activity, int):
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

        if isinstance(price, (int, float)):
            self.__price = price
        else:
            raise Exception("price must be of type : int or float ")

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

    # constructor

    # argument activities_edges is a list of lists each list represents an arc [A1 , A2 , 0 or 1 or -1]
    def __init__(self, activities_edges , candidates):
        self.G = nx.DiGraph()
        self.G.add_weighted_edges_from(activities_edges)
        for act, candidate in enumerate(candidates)  :
            self.G.nodes[act]["service"] = random.sample(candidate, 1)[0]


    # Calcul Methods

    def cpResponseTime(self,rootAct = 0):
        try:
            outgoing = list(self.G.successors(rootAct)) # outgoing arcs
            neighbor = outgoing[0]  # first neighbor
            type = self.G.edges(rootAct,neighbor)["weight"]
            if type == 0:
                # type = sequential
                return self.G.nodes[rootAct]["service"].getResponseTime() + self.cpResponseTime(neighbor)
            elif type == -1:
                # type = conditional
                s = 0
                n = 0
                for arc in outgoing :
                    n += 1
                    s += self.cpResponseTime(neighbor)
                return (s / n) + self.G.nodes[rootAct]["service"].getResponseTime()
            elif type == 1:
                # type = parallel
                return self.G.nodes[rootAct]["service"].getResponseTime() + max([self.cpResponseTime(neighbor) for arc in outgoing])
        except KeyError:  # node with no destination
            self.G.nodes[rootAct]["service"].getResponseTime()

    def cpPrice(self,rootAct = 0):
        try:
            outgoing = list(self.G.successors(rootAct)) # outgoing arcs
            neighbor = outgoing[0]  # first neighbor
            type = self.G.edges(rootAct,neighbor)["weight"]

            if type == 0:
                # type = sequentials
                return self.G.nodes[rootAct]["service"].getResponseTime() + self.cpResponseTime(neighbor)

            elif type == -1:
                # type = conditional
                s = 0
                n = 0
                for arc in outgoing :
                    n += 1
                    s += self.cpResponseTime(neighbor)
                return (s / n) + self.G.nodes[rootAct]["service"].getResponseTime()
            elif type == 1:
                # type = parallel
                return self.G.nodes[rootAct]["service"].getResponseTime() + max([self.cpResponseTime(neighbor) for arc in outgoing])
        except KeyError:
            self.G.nodes[rootAct]["service"].getResponseTime()

    def cpAvailability(self, rootAct=0):
        try:
            outgoing = list(self.G.successors(rootAct))  # outgoing arcs
            neighbor = outgoing[0]  # first neighbor
            type = self.G.edges(rootAct, neighbor)["weight"]
            if type == 0:
                # type = sequential
                return return self.G[rootAct]["service"].getAvailability() * self.cpAvailability(neighbor)
            elif type == -1:
                # type = conditional
                s = 0
                n = 0
                for arc in outgoing:
                    n += 1
                    s += self.cpAvailability(neighbor)
                return (s / n) * self.G.nodes[rootAct]["service"].getAvailability()
            elif type == 1:
                # type = parallel
                return self.G.nodes[rootAct]["service"].getAvailability() * prod([self.cpAvailability()(neighbor) for arc in outgoing])
        except KeyError:  # node with no destination
            return self.G.nodes[rootAct]["service"].getAvailability()

    def cpReliability(self, rootAct=0):
        try:
            outgoing = list(self.G.successors(rootAct))  # outgoing arcs
            neighbor = outgoing[0]  # first neighbor
            type = self.G.edges(rootAct, neighbor)["weight"]
            if type == 0:
                # type = sequential
                return return self.G[rootAct]["service"].getReliability() * self.cpReliability(neighbor)
            elif type == -1:
                # type = conditional
                s = 0
                n = 0
                for arc in outgoing:
                    n += 1
                    s += self.cpReliability(neighbor)
                return (s / n) * self.G.nodes[rootAct]["service"].getReliability()
            elif type == 1:
                # type = parallel
                return self.G.nodes[rootAct]["service"].getReliability() * prod([self.cpReliability()(neighbor) for arc in outgoing])
        except KeyError:  # node with no destination
            return self.G.nodes[rootAct]["service"].getReliability()

    # Quality of Service

    def globalQos(self, minQos, maxQos, constraints, weightList):  # weightList should be in order (Price,ResponseTime,Availability,Reliability)

        drt = constraints['responseTime'] - self.cpResponseTime()
        dpr = constraints['price'] - self.cpPrice()
        dav = self.cpAvailability() - constraints['availability']
        drel = self.cpReliability() - constraints['reliability']
        if drt and dpr and dav and drel:
            rt = (maxQos['responseTime'] - self.cpResponseTime()) / (maxQos['responseTime'] - minQos['responseTime'])
            pr = (maxQos['price'] - self.cpPrice()) / (maxQos['price'] - minQos['price'])
            av = (self.cpAvailability() - minQos['availability']) / (maxQos['availability'] - minQos['availability'])
            rel = (self.cpReliability() - minQos['reliability']) / (maxQos['reliability'] - minQos['reliability'])

            vect1 = numpy.array([rt, pr, av, rel])
            # weights
            vect2 = numpy.array(weightList)
            # vectorial product
            return numpy.dot(vect1, vect2)
        else:
            return -1

    # Matching degree
    def cpMatching(self, rootAct=0):
        n = G.number_of_nodes()
        try:
            outgoing = list(self.G.successors(rootAct))  # outgoing arcs
            s = sum([self.cpMatching(neighbor) for neighbor in outgoing])
            return s + (self.G.nodes[rootAct]["service"].getMatching() / servNumber)
        except KeyError:
            return self.G.nodes[rootAct]["service"].getMatching() / n

    # Modifying composition plan by mutating a service

    def mutate(self,new):
        self.G.nodes[new.getActivity()]["service"] = new



# CROSSOVER

def crossover(Plan1, Plan2):
    activities_edges = list(Plan1.G.edges.data("weight"))
    candidates = [act[1] for act in list(Plan1.G.nodes.data("service"))]
    child = CompositionPlan(activities_edges , candidates)
    for act in child.G.nodes:  # Selecting services to mutate
        if random.randint(0, 1):  # 50 % chance of mutation
                child.G.nodes[act]["service"] = Plan2.G.nodes[act]["service"]
    return child
