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
            self.G.nodes[act]["visited"] = False      # this attribut is used for calculating qos once per node
        self.__actNum = self.G.number_of_nodes()        # number of activities
        self.__qos = None  # not initialized
        self.__matching = None # not initialized



    # Quality of Service

    # rootAct parameter is used for recursive calls
    def cpQos(self,rootAct=0):
        if self.__qos != None :
            return self.__qos

        if self.G.nodes[rootAct]["visited"] :   # checking if this node has been visited before
            return {'responseTime' : 0 , 'price' : 0 , 'availability' : 1 , 'reliability' : 1}

        try:
            self.G.nodes[rootAct]["visited"] = True
            outgoing = list(self.G.successors(rootAct))  # outgoing arcs
            neighbor = outgoing[0]  # first outgoing arc
            type = self.G.edges[rootAct, neighbor]["weight"] # type of the arc
            if type == 0:
                # type = sequential
                qos = self.cpQos(neighbor)
                qos['responseTime'] += self.G.nodes[rootAct]["service"].getResponseTime()
                qos['price'] += self.G.nodes[rootAct]["service"].getPrice()
                qos['availability'] *= self.G.nodes[rootAct]["service"].getAvailability()
                qos['reliability'] *= self.G.nodes[rootAct]["service"].getReliability()

            elif type == -1:
                # type = conditional
                s1 = 0
                s2 = 0
                s3 = 1
                s4 = 1
                n = 0
                for neighbor in outgoing:
                    qos = self.cpQos(neighbor)
                    n += 1
                    s1 += qos['responseTime']
                    s2 += qos['price']
                    s3 += qos['availability']
                    s4 += qos['reliability']

                qos['responseTime'] = (s1 / n) + self.G.nodes[rootAct]["service"].getResponseTime()
                qos['price'] = (s2 / n) + self.G.nodes[rootAct]["service"].getPrice()
                qos['availability'] = (s3 / n) * self.G.nodes[rootAct]["service"].getAvailability()
                qos['reliability'] = (s4 / n) * self.G.nodes[rootAct]["service"].getReliability()

            elif type == 1:
                # type = parallel
                l1 , l2 , l3 , l4 = [] , [] , [] , []
                for neighbor in outgoing :
                    qos = self.cpQos(neighbor)
                    l1.append(qos['responseTime'])
                    l2.append(qos['price'])
                    l3.append(qos['availability'])
                    l4.append(qos['reliability'])

                qos['responseTime'] = self.G.nodes[rootAct]["service"].getResponseTime() + max(l1)
                qos['price'] = self.G.nodes[rootAct]["service"].getPrice() + sum(l2)
                qos['availability'] = self.G.nodes[rootAct]["service"].getAvailability() * prod(l3)
                qos['reliability'] = self.G.nodes[rootAct]["service"].getReliability() * prod(l4)


        except IndexError :  # node with no destination
            qos = {}
            qos['responseTime'] = self.G.nodes[rootAct]["service"].getResponseTime()
            qos['price'] = self.G.nodes[rootAct]["service"].getPrice()
            qos['availability'] = self.G.nodes[rootAct]["service"].getAvailability()
            qos['reliability'] = self.G.nodes[rootAct]["service"].getReliability()
            return qos

        if rootAct == 0 :  # reversing visited attribut of each node to False - final step
            for act in range(self.__actNum) :
                self.G.nodes[act]["visited"] = False
            self.qos = qos  # storing qos in attribut

        return qos

    # Matching degree
    def cpMatching(self):
        if self.__matching != None :
            return self.__matching
        # sum of matching degree of each service
        s = sum([self.G.nodes[i]["service"].getMatching() for i in range(self.__actNum)])
        return s / self.__actNum

    # cloning composition plan
    def clone(self) :
        actGraph = list(self.G.edges.data("weight"))  # getting graph arcs
        services = [[act[1]] for act in list(self.G.nodes.data("service"))] # getting services
        clone = CompositionPlan(actGraph, services)
        return clone
