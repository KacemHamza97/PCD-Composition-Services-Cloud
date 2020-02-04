import numpy
from math import sqrt
import networkx as nx
from random import randint , sample
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
            raise Exception("activity must be of type : int or float ")

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

        return sqrt(dRes ** 2 + dPri ** 2 + dRel ** 2 + dAva ** 2)

    ##### class CompositionPlan #####


class CompositionPlan:

    # constructor

    # argument actGraph is a list of lists each list represents an arc [A1 , A2 , 0 or 1 or -1]
    def __init__(self, actGraph, candidates):
        self.G = nx.DiGraph()
        self.G.add_weighted_edges_from(actGraph)
        for act, candidate in enumerate(candidates):
            self.G.nodes[act]["service"] = sample(candidate, 1)[0]
            self.G.nodes[act]["visited"] = False
        self.visited = 0

    # Calcul Methods

    # def cpResponseTime(self, rootAct=0):
    #     if self.G.nodes[rootAct]["visited"] :
    #         return 0
    #     try:
    #         self.visited += 1
    #         self.G.nodes[rootAct]["visited"] = True
    #         if self.visited == self.G.number_of_nodes() :
    #             self.visited = 0
    #             for i in range(self.G.number_of_nodes()) :
    #                 self.G.nodes[i]["visited"] = False
    #         outgoing = list(self.G.successors(rootAct))  # outgoing arcs
    #         neighbor = outgoing[0]  # first neighbor
    #         type = self.G.edges[rootAct, neighbor]["weight"]
    #         if type == 0:
    #             # type = sequential
    #             return  self.G.nodes[rootAct]["service"].getResponseTime() + self.cpResponseTime(neighbor)
    #         elif type == -1:
    #             # type = conditional
    #             s = 0
    #             n = 0
    #             for neighbor in outgoing:
    #                 n += 1
    #                 s += self.cpResponseTime(neighbor)
    #             return (s / n) + self.G.nodes[rootAct]["service"].getResponseTime()
    #         elif type == 1:
    #             # type = parallel
    #             return self.G.nodes[rootAct]["service"].getResponseTime() + max([self.cpResponseTime(neighbor) for neighbor in outgoing])
    #
    #     except IndexError :  # node with no destination
    #         return self.G.nodes[rootAct]["service"].getResponseTime()
    #
    # def cpPrice(self, rootAct=0):
    #     if self.G.nodes[rootAct]["visited"] :
    #         return 0
    #     try:
    #         self.visited += 1
    #         self.G.nodes[rootAct]["visited"] = True
    #         if self.visited == self.G.number_of_nodes() :
    #             self.visited = 0
    #             for i in range(self.G.number_of_nodes()) :
    #                 self.G.nodes[i]["visited"] = False
    #         outgoing = list(self.G.successors(rootAct))  # outgoing arcs
    #         neighbor = outgoing[0]  # first neighbor
    #         type = self.G.edges[rootAct, neighbor]["weight"]
    #
    #         if type == 0:
    #             # type = sequentials
    #             return self.G.nodes[rootAct]["service"].getPrice() + self.cpPrice(neighbor)
    #
    #         elif type == -1:
    #             # type = conditional
    #             s = 0
    #             n = 0
    #             for neighbor in outgoing:
    #                 n += 1
    #                 s += self.cpPrice(neighbor)
    #             return (s / n) + self.G.nodes[rootAct]["service"].getPrice()
    #         elif type == 1:
    #             # type = parallel
    #             return self.G.nodes[rootAct]["service"].getPrice() + sum([self.cpPrice(neighbor) for neighbor in outgoing])
    #     except IndexError :
    #         return self.G.nodes[rootAct]["service"].getPrice()
    #
    #
    #
    # def cpAvailability(self, rootAct=0):
    #     if self.G.nodes[rootAct]["visited"] :
    #         return 1
    #     try :
    #         self.visited += 1
    #         self.G.nodes[rootAct]["visited"] = True
    #         if self.visited == self.G.number_of_nodes() :
    #             self.visited = 0
    #             for i in range(self.G.number_of_nodes()) :
    #                 self.G.nodes[i]["visited"] = False
    #         outgoing = list(self.G.successors(rootAct))  # outgoing arcs
    #         neighbor = outgoing[0]  # first neighbor
    #         type = self.G.edges[rootAct, neighbor]["weight"]
    #         if type == 0:
    #             # type = sequential
    #             return self.G.nodes[rootAct]["service"].getAvailability() * self.cpAvailability(neighbor)
    #         elif type == -1:
    #             # type = conditional
    #             s = 0
    #             n = 0
    #             for neighbor in outgoing:
    #                 n += 1
    #                 s += self.cpAvailability(neighbor)
    #             return (s / n) * self.G.nodes[rootAct]["service"].getAvailability()
    #         elif type == 1:
    #             # type = parallel
    #             return self.G.nodes[rootAct]["service"].getAvailability() * prod([self.cpAvailability(neighbor) for neighbor in outgoing])
    #     except IndexError :  # node with no destination
    #         return self.G.nodes[rootAct]["service"].getAvailability()
    #
    # def cpReliability(self, rootAct=0):
    #     if self.G.nodes[rootAct]["visited"] :
    #         return 1
    #     try:
    #         self.visited += 1
    #         self.G.nodes[rootAct]["visited"] = True
    #         if self.visited == self.G.number_of_nodes() :
    #             self.visited = 0
    #             for i in range(self.G.number_of_nodes()) :
    #                 self.G.nodes[i]["visited"] = False
    #         outgoing = list(self.G.successors(rootAct))  # outgoing arcs
    #         neighbor = outgoing[0]  # first neighbor
    #         type = self.G.edges[rootAct, neighbor]["weight"]
    #         if type == 0:
    #             # type = sequential
    #             return self.G.nodes[rootAct]["service"].getReliability() * self.cpReliability(neighbor)
    #         elif type == -1:
    #             # type = conditional
    #             s = 0
    #             n = 0
    #             for neighbor in outgoing:
    #                 n += 1
    #                 s += self.cpReliability(neighbor)
    #             return (s / n) * self.G.nodes[rootAct]["service"].getReliability()
    #         elif type == 1:
    #             # type = parallel
    #             return self.G.nodes[rootAct]["service"].getReliability() * prod([self.cpReliability(neighbor) for neighbor in outgoing])
    #     except IndexError  :  # node with no destination
    #         return self.G.nodes[rootAct]["service"].getReliability()



    # Quality of Service

    def cpQos(self,rootAct=0):
        if self.G.nodes[rootAct]["visited"] :
            return {'responseTime' : 0 , 'price' : 0 , 'availability' : 1 , 'reliability' : 1}

        try:
            self.visited += 1
            self.G.nodes[rootAct]["visited"] = True
            if self.visited == self.G.number_of_nodes() :
                self.visited = 0
                for i in range(self.G.number_of_nodes()) :
                    self.G.nodes[i]["visited"] = False
            outgoing = list(self.G.successors(rootAct))  # outgoing arcs
            neighbor = outgoing[0]  # first neighbor
            type = self.G.edges[rootAct, neighbor]["weight"]
            if type == 0:
                # type = sequential
                QosDict = self.cpQos(neighbor)
                QosDict['responseTime'] += self.G.nodes[rootAct]["service"].getResponseTime()
                QosDict['price'] += self.G.nodes[rootAct]["service"].getPrice()
                QosDict['availability'] *= self.G.nodes[rootAct]["service"].getAvailability()
                QosDict['reliability'] *= self.G.nodes[rootAct]["service"].getReliability()
                return QosDict
            elif type == -1:
                # type = conditional
                s1 = 0
                s2 = 0
                s3 = 1
                s4 = 1
                n = 0
                for neighbor in outgoing:
                    n += 1
                    QosDict = self.cpQos(neighbor)
                    s1 += QosDict['responseTime']
                    s2 += QosDict['price']
                    s3 *= QosDict['availability']
                    s4 *= QosDict['reliability']
                QosDict = {}
                QosDict['responseTime'] = (s1 / n) + self.G.nodes[rootAct]["service"].getResponseTime()
                QosDict['price'] = (s2 / n) + self.G.nodes[rootAct]["service"].getPrice()
                QosDict['availability'] = (s3 / n) * self.G.nodes[rootAct]["service"].getAvailability()
                QosDict['reliability'] = (s4 / n) * self.G.nodes[rootAct]["service"].getReliability()
                return QosDict
            elif type == 1:
                # type = parallel
                l1 , l2 , l3 , l4 = [] , [] , [] , []
                for neighbor in outgoing :
                    QosDict = self.cpQos(neighbor)
                    l1.append(QosDict['responseTime'])
                    l2.append(QosDict['price'])
                    l3.append(QosDict['availability'])
                    l4.append(QosDict['reliability'])
                QosDict = {}
                QosDict['responseTime'] = self.G.nodes[rootAct]["service"].getResponseTime() + max(l1)
                QosDict['price'] = self.G.nodes[rootAct]["service"].getPrice() + sum(l2)
                QosDict['availability'] = self.G.nodes[rootAct]["service"].getAvailability() * prod(l3)
                QosDict['reliability'] = self.G.nodes[rootAct]["service"].getReliability() * prod(l4)

                return QosDict

        except IndexError :  # node with no destination
            QosDict = {}
            QosDict['responseTime'] = self.G.nodes[rootAct]["service"].getResponseTime()
            QosDict['price'] = self.G.nodes[rootAct]["service"].getPrice()
            QosDict['availability'] = self.G.nodes[rootAct]["service"].getAvailability()
            QosDict['reliability'] = self.G.nodes[rootAct]["service"].getReliability()
            return QosDict

    def globalQos(self, minQos, maxQos, constraints, weightList):  # weightList should be in order (Price,ResponseTime,Availability,Reliability)

        QosDict = self.cpQos()

        drt = constraints['responseTime'] - QosDict['responseTime']
        dpr = constraints['price'] - QosDict['price']
        dav = QosDict['availability'] - constraints['availability']
        drel = QosDict['reliability'] - constraints['reliability']

        if drt and dpr and dav and drel:
            rt = (maxQos['responseTime'] - QosDict['responseTime']) / (maxQos['responseTime'] - minQos['responseTime'])
            pr = (maxQos['price'] - QosDict['price']) / (maxQos['price'] - minQos['price'])
            av = (QosDict['availability'] - minQos['availability']) / (maxQos['availability'] - minQos['availability'])
            rel = (QosDict['reliability'] - minQos['reliability']) / (maxQos['reliability'] - minQos['reliability'])

            vect1 = numpy.array([rt, pr, av, rel])
            # weights
            vect2 = numpy.array(weightList)
            # vectorial product
            return numpy.dot(vect1, vect2)
        else:
            return -1

    # Matching degree
    def cpMatching(self):
        n = self.G.number_of_nodes()
        s = sum([self.G.nodes[i]["service"].getMatching() for i in range(n)])
        return s/n

    # Modifying composition plan by mutating a service

    def mutate(self, new):
        self.G.nodes[new.getActivity()]["service"] = new


# CROSSOVER

def crossover(Plan1, Plan2):
    actGraph = list(Plan1.G.edges.data("weight"))
    candidates = [[act[1]] for act in list(Plan1.G.nodes.data("service"))]
    child = CompositionPlan(actGraph, candidates)
    for act in child.G.nodes:  # Selecting services to mutate
        if randint(0, 1):  # 50 % chance of mutation
            child.G.nodes[act]["service"] = Plan2.G.nodes[act]["service"]
    return child
