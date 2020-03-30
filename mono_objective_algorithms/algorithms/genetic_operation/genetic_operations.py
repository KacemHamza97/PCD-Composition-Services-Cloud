from random import random


# mutation
def mutate(cp, new_service):
    new_cp = cp.clone()
    # new_service is added to the composition plan
    new_cp.G.nodes[new_service.getActivity()]["service"] = new_service
    return new_cp


# Crossover
def crossover(parent1, parent2, pc):
    child = parent1.clone()  # creating new child identical to first parent
    # modifying child
    for act in child.G.nodes:  # Selecting service to replace
        if random() <= pc:  # pc : probability of crossover
            # replacing with service from second parent
            child.G.nodes[act]["service"] = parent2.G.nodes[act]["service"]
    return child
