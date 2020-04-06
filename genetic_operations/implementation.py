from random import random, randint
from numpy.random import choice


# +----------------------------------------------------------------------------------------------+#

# mutation
def mutate(cp, new_service):
    new_cp = cp.clone()
    # new_service is added to the composition plan
    new_cp.G.nodes[new_service.getActivity()]["service"] = new_service
    return new_cp


# +----------------------------------------------------------------------------------------------+#

# Crossover
def crossover(parent1, parent2, pc):
    offspring = parent1.clone()
    # modifying offspring
    for act in offspring.G.nodes:  # Selecting service to replace
        if random() <= pc:  # pc : probability of crossover
            # replacing with service from second parent
            offspring.G.nodes[act]["service"] = parent2.G.nodes[act]["service"]
    return offspring


# +----------------------------------------------------------------------------------------------+#

# BSG
def BSG(cp1, cp2, constraints, candidates):  # constraints are added to avoid creating offsprings in vain

    def crossover(cp1 , cp2 ) :

        offspring = cp1.clone()

        while 1:
            x1 = randint(0, cp2.getNumberOfActivities() - 2)
            x2 = randint(x1 + 1, cp2.getNumberOfActivities() - 1)
            for act in range(x1, x2 + 1):  # Selecting service to replace
                # replacing with service from second parent
                offspring.G.nodes[act]["service"] = cp2.G.nodes[act]["service"]
            if offspring.verifyConstraints(constraints)  :
                break

        return offspring

    def mutate(cp) : 

        offspring = cp1.clone()

        # choose randomly a service to mutate
        service = offspring.randomService()
        while 1:
            new = choice(candidates[service.getActivity()])
            # mutation operation
            offspring.G.nodes[new.getActivity()]["service"] = new
            if offspring.verifyConstraints(constraints)  :
                break

        return offspring
        

    offspringsList = []

    # Crossover

    # First offspring

    offspringsList.append(crossover(cp1 , cp2))

    # Second offspring

    while 1 : 
        offspring = crossover(cp2 , cp1)
        if offspring not in offspringsList : 
            break

    offspringsList.append(offspring)

    # Mutation

    # First offspring

    while 1 : 
        offspring = mutate(cp1)
        if offspring not in offspringsList : 
            break
        
    offspringsList.append(offspring)

    # Second offspring

    while 1 : 
        offspring = mutate(cp2)
        if offspring not in offspringsList : 
            break
        
    offspringsList.append(offspring)

    return(offspringsList)
