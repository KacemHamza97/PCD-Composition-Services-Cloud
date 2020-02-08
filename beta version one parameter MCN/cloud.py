from math import sqrt
import networkx as nx
from random import sample
from functools import reduce


# product of given list elements

def prod(List):
    return reduce((lambda x, y: x * y), List)


    #### class Service ####
class Service:

    # constructor

    def __init__(self, activity, responseTime, reliability, availability, price, matching=1):

        self.__activity = activity
        self.__responseTime = responseTime
        self.__reliability = reliability
        self.__availability = availability
        self.__price = price
        self.__matching = matching

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

        drt = self.__responseTime - service.getResponseTime()
        dpr = self.__price - service.getPrice()
        drel = self.__reliability - service.getReliability()
        dav = self.__availability - service.getAvailability()

        return sqrt(drt ** 2 + dpr ** 2 + drel ** 2 + dav ** 2)

    ##### class CompositionPlan #####


class CompositionPlan:

    # constructor

    def __init__(self, actGraph, candidates):
        self.G = nx.DiGraph()         # Graph attribut
        self.G.add_weighted_edges_from(actGraph)
        for act, candidate in enumerate(candidates):  # Generating random services from candidates
            self.G.nodes[act]["service"] = sample(candidate, 1)[0]
            self.G.nodes[act]["visited"] = False      # this attribut is used for calculating Qos once per node
        self.actNum = self.G.number_of_nodes()        # number of activities

    # Quality of Service

    # rootAct parameter is used for recursive calls
    def cpQos(self,rootAct=0):

        if self.G.nodes[rootAct]["visited"] :   # checking if this node has been visited before
            return {'responseTime' : 0 , 'price' : 0 , 'availability' : 1 , 'reliability' : 1}

        try:
            self.G.nodes[rootAct]["visited"] = True
            outgoing = list(self.G.successors(rootAct))  # outgoing arcs
            neighbor = outgoing[0]  # first outgoing arc
            type = self.G.edges[rootAct, neighbor]["weight"] # type of the arc
            if type == 0:
                # type = sequential
                QosDict = self.cpQos(neighbor)
                QosDict['responseTime'] += self.G.nodes[rootAct]["service"].getResponseTime()
                QosDict['price'] += self.G.nodes[rootAct]["service"].getPrice()
                QosDict['availability'] *= self.G.nodes[rootAct]["service"].getAvailability()
                QosDict['reliability'] *= self.G.nodes[rootAct]["service"].getReliability()

            elif type == -1:
                # type = conditional
                s1 = 0
                s2 = 0
                s3 = 1
                s4 = 1
                n = 0
                for neighbor in outgoing:
                    QosDict = self.cpQos(neighbor)
                    n += 1
                    s1 += QosDict['responseTime']
                    s2 += QosDict['price']
                    s3 += QosDict['availability']
                    s4 += QosDict['reliability']

                QosDict['responseTime'] = (s1 / n) + self.G.nodes[rootAct]["service"].getResponseTime()
                QosDict['price'] = (s2 / n) + self.G.nodes[rootAct]["service"].getPrice()
                QosDict['availability'] = (s3 / n) * self.G.nodes[rootAct]["service"].getAvailability()
                QosDict['reliability'] = (s4 / n) * self.G.nodes[rootAct]["service"].getReliability()

            elif type == 1:
                # type = parallel
                l1 , l2 , l3 , l4 = [] , [] , [] , []
                for neighbor in outgoing :
                    QosDict = self.cpQos(neighbor)
                    l1.append(QosDict['responseTime'])
                    l2.append(QosDict['price'])
                    l3.append(QosDict['availability'])
                    l4.append(QosDict['reliability'])

                QosDict['responseTime'] = self.G.nodes[rootAct]["service"].getResponseTime() + max(l1)
                QosDict['price'] = self.G.nodes[rootAct]["service"].getPrice() + sum(l2)
                QosDict['availability'] = self.G.nodes[rootAct]["service"].getAvailability() * prod(l3)
                QosDict['reliability'] = self.G.nodes[rootAct]["service"].getReliability() * prod(l4)

            if rootAct == 0 :  # reversing visited attribut of each node to False - final step
                for act in range(self.actNum) :
                    self.G.nodes[act]["visited"] = False
            return QosDict

        except IndexError :  # node with no destination
            QosDict = {}
            QosDict['responseTime'] = self.G.nodes[rootAct]["service"].getResponseTime()
            QosDict['price'] = self.G.nodes[rootAct]["service"].getPrice()
            QosDict['availability'] = self.G.nodes[rootAct]["service"].getAvailability()
            QosDict['reliability'] = self.G.nodes[rootAct]["service"].getReliability()
            return QosDict

    # Matching degree
    def cpMatching(self):
        # sum of matching degree of each service
        s = sum([self.G.nodes[i]["service"].getMatching() for i in range(self.actNum)])
        return s / self.actNum
