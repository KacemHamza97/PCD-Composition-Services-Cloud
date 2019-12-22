import numpy 
import math

# product of giving list elements

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

	def __init__(self, activity , responseTime, reliability, availability, productList , matching = 1):

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
            
		if isinstance(matching,(int,float)) and 0 < matching <= 1 :
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
	
	def euclideanDist (self , service ) :
		
		dRes = self.__responseTime - service.getResponseTime()
		dPri = self.__price - service.getPrice()
		dRel = self.__reliability - service.getReliability()
		dAva = self.__availability - service.getAvailability()
		
		return math.sqrt(dRes**2 + dPri**2 + dRel**2 + dAva**2)
		
        


													
													
								##### class workflow #####

class WorkFlow:

    # constructor   
    
    # argument servGraph is a list of tuples each tuple represents an arc (S1,S2,[0,1,-1])

	def __init__(self, rootServ , servGraph):
		self.rootServ = rootServ    
		self.servGraph = {}                    # Dicitonary : source service is a key ,list of destination services and type are values
		self.servSet = set()                   # set of services present in the Graph
		for i in servGraph:
			self.servSet.add(i[0])
			self.servSet.add(i[1])
			if i[0] not in self.servGraph.keys():          # creating non-exisitent key 
				self.servGraph[i[0]] = [[i[1], i[2]]]
			else:
				self.servGraph[i[0]].append([i[1], i[2]])  # Appending existent value with a new destination

		
	# Calcul Methods

	def evaluateResponseTime(self,rootServ = None):
		if rootServ == None :
			rootServ = self.rootServ
		servGraph = self.servGraph
		if rootServ not in servGraph.keys():     # node with no destination
			return rootServ.getResponseTime() 
		else:
			outgoing = servGraph[rootServ]		  # outgoing arcs
			arc = outgoing[0]         	  # first arc 
			# dest = arc[0]                   
			# type = arc[1]				  
			if arc[1] == 0:                     
				# type = sequential
				return rootServ.getResponseTime() + self.evaluateResponseTime(arc[0])
			elif arc[1] == -1:					
				# type = conditional
				s = 0
				n = 0
				for arc in outgoing :
					n += 1
					s += self.evaluateResponseTime(arc[0])
				return (s / n) + rootServ.getResponseTime()
			elif arc[1] == 1:							
				# type = parallel
				return rootServ.getResponseTime() + max([self.evaluateResponseTime(arc[0]) for arc in outgoing])
	
	
	def evaluatePrice(self,rootServ = None):
		if rootServ == None :
			rootServ = self.rootServ
		servGraph = self.servGraph
		if rootServ not in servGraph.keys():     # node with no destination
			return rootServ.getPrice()
		else:
			outgoing = servGraph[rootServ]		  # outgoing arcs
			arc = outgoing[0]         	  # first arc 
			# dest = arc[0]                   
			# type = arc[1]				 
			if arc[1] == 0:
				# type = sequential
				return rootServ.getPrice() + self.evaluatePrice(arc[0])

			elif arc[1] == -1:
				# type = conditional
				s = 0
				n = 0
				for arc in outgoing:
					n += 1
					s += self.evaluatePrice(arc[0])
				return (s / n) + rootServ.getPrice()
			elif arc[1] == 1:
				# type = parallel
				return rootServ.getPrice() + sum([self.evaluatePrice(arc[0]) for arc in outgoing])


	def evaluateAvailability(self,rootServ = None):
		if rootServ == None :
			rootServ = self.rootServ
		servGraph = self.servGraph
		if rootServ not in servGraph.keys():    # node with no destination
			return rootServ.getAvailability()
		else:
			outgoing = servGraph[rootServ]		  # outgoing arcs
			arc = outgoing[0]         	  # first arc 
			# dest = arc[0]                   
			# type = arc[1]				  
			if arc[1] == 0:
				# type = sequential
				return rootServ.getAvailability() * self.evaluateAvailability(arc[0])
			elif arc[1] == -1:
				# type = conditional
				s = 0
				n = 0
				for arc in outgoing:
					n += 1
					s += self.evaluateAvailability(arc[0])
				return (s / n) * rootServ.getAvailability()
			elif arc[1] == 1:
				# type = parallel
				return rootServ.getAvailability() * prod([self.evaluateAvailability(arc[0]) for arc in outgoing])


	def evaluateReliability(self,rootServ = None):
		if rootServ == None :
			rootServ = self.rootServ
		servGraph = self.servGraph
		if rootServ not in servGraph.keys():   # node with no destination
			return rootServ.getReliability()
		else:
			outgoing = servGraph[rootServ]	  # outgoing arcs
			arc = outgoing[0]         	  # first arc 
			# dest = arc[0]                   
			# type = arc[1]				 
			if arc[1] == 0:
				# type = sequential
				return rootServ.getReliability() * self.evaluateReliability(arc[0])
			elif arc[1] == -1:
				# type = conditional
				s = 0
				n = 0
				for arc in outgoing:
					n += 1
					s += self.evaluateReliability(arc[0])
				return (s / n) * rootServ.getReliability()
			elif arc[1] == 1:
				# type = parallel
				return rootServ.getReliability() * prod([self.evaluateReliability(arc[0]) for arc in outgoing])


	# Quality of Service 

	def QoS(self,weightList=[1, 1, 1, 1]):     # weightList should be in order (Price,ResponseTime,Availability,Reliability)
		# criteria 
		vect1 = numpy.array([self.evaluatePrice(), self.evaluateResponseTime(),self.evaluateAvailability(),self.evaluateReliability()])
		# weights 
		vect2 = numpy.array(weightList)
		# vectorial product
		return numpy.dot(vect1, vect2)
		
		
	# Matching degree
	
		
	def evaluateMatching(self,rootServ = None) :
		if rootServ == None :
			rootServ = self.rootServ
		servGraph = self.servGraph
		servNumber = len(self.servSet)          
		if rootServ not in servGraph.keys():    # node with no destination
			return rootServ.getMatching() / servNumber
		else:
			outgoing = servGraph[rootServ]      # list of arcs linked to rootServ
			s = 0
			for arc in outgoing:
				s += self.evaluateMatching(arc[0])
			return s + (rootServ.getMatching() / servNumber)
			
			
			
	
	# Modifying workflow by mutating a service
	
	def mutate ( self , target , new ) :
		if target.getActivity() == new.getActivity() :            # Activity matching true
			self.servSet.remove(target)							  # Updating servSet
			self.servSet.add(new)
			if self.rootServ == target :								
				self.servGraph[new] = self.servGraph.pop(self.rootServ)
				self.rootServ = target										# if target is rootServ than update attribut
			else :
				for service in self.servGraph.keys() : 
					if service == target :
						self.servGraph[new] = self.servGraph.pop(service)  # replacing old service with new and keeping outgoing arcs 
				
					else :
						for arc in self.servGraph[service] : 
							if arc[0] == target :                          # replacing old service if found in other arcs
								arc[0] = new
								break 
		else :
			raise Exception("Activity mismatch !")
						
						
	# Modifying workflow by workflow-CROSSOVER (half of activities mutation )
	
	def crossover ( self , workflow ) :
		mutationNumber = 0 
		for new in workflow.servSet :                          # Selecting services from 2nd workflow (parameter)
			if( mutationNumber < len(self.servSet)//2 ) :      # no more than half of the services mutated
				for target in self.servSet :				   
					if target.getActivity() == new.getActivity() :    # Searching for matching targets
						self.mutate(target,new)                # Mutate
						mutationNumber += 1                         
			else : 
				break
						
	
		
		
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

		
	
    
    

