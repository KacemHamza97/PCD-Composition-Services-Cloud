import cloud 
import copy

# services is a list made of list of services that perform a common activity , each list of services represents an activity  
# services is indexed based on the attribut activity of each service (cloud.py)
# actGraph is a graph with only activities indexes linked to each other by arcs
# rootAct is the first activity

# sort neighbors of service based on euclidean distance from the nearest to the furthest

def getNeighbors (s,services) :   # s is a service
	candidates = services[s.getActivity()-1]
	return sorted([neighbor for neighbor in candidates if neighbor != s], key = lambda x : s.euclideanDist(x))		
			



# SC : condition for scouts , MCN : termination condition , SN : number of workflows , p :probability
def ABCgenetic (rootAct , actGraph , services , SQ , MCN , SN , p) :   
	
	#initializing
	
	solutions = list() 
	fitnessList = list()
	probabilityList = list(0 for i in range(SN))
	limit = list(0 for i in range(SN))
	bestTwo = list()
	CP = 4 * MCN / 5       # changing point for scouts
	
	# solutions and fitness initializing
	
	for i in range(SN) : 
		solutions.append(cloud.randomWorkFlow(rootAct,actGraph,services))
		fitnessList.append(solutions[i].QoS())
	
			
		
	# Algorithm
	for itera in range(1,MCN+1) :
		
		# working bees phase
		for i in range(SN) :        
			s = solutions[i]					#s is a workflow
			new = copy.deepcopy(s)             # copy of current workflow
			# choose randomly a service to mutate
			service = new.randomServ()
			# new service index
			neighbors = getNeighbors(service,services)
			N = len(neighbors)
			index = (N-1) // itera 
			# mutation
			new.mutate (service , neighbors[index])
			Q = new.QoS()
			if Q > fitnessList[i] :
				solutions[i] = new
				fitnessList[i] = Q
				limit[i] = 0 
			else :
				limit[i] += 1
			
			
		# Probability update
		for i in range(SN) :
			s = solutions[i]
			probabilityList[i] = s.QoS() / sum(fitnessList)
			
		
		# onlooker bees phase 
		for i in range(SN) : 
			if probabilityList[i] > p :    
				s = solutions[i]					#s is a workflow
				new = copy.deepcopy(s)             # copy of current workflow
				# choose randomly a service to mutate
				service = new.randomServ()
				# new service index
				neighbors = getNeighbors(service,services)
				N = len(neighbors)
				index = (N-1) // itera
				# mutation
				new.mutate (service , neighbors[index])
				Q = new.QoS()
				if Q > fitnessList[i] :
					solutions[i] = new
					fitnessList[i] = Q
					limit[i] = 0
				else :
					limit[i] += 1
					
					
		# scout bees phase 
		for i in range(SN) :
			s = solutions[i]
			if limit[i] == SQ :   # scouts bee condition verified
				if itera >= CP :
					# Best two solutions so far
					AUX = copy.deepcopy(solutions)
					S1 = max (AUX , key = lambda x : x.QoS())
					AUX.remove(S1)
					S2 = max (AUX , key = lambda x : x.QoS())
					index = solutions.index(S2)
					# Crossover
					S1.crossover(S2)
					solutions[index] = S1
				
				else :
					# Scouting 
					solutions.append(cloud.randomWorkFlow(rootAct,actGraph,services))
					fitnessList.append(solutions[i].QoS())
					
					
	return max (solutions , key = lambda x : x.QoS())				
		
		
		
			 	
	
