import cloud as cl

p1 = cl.Product(12,30)
p2 = cl.Product(5,50)

s1 = cl.Service(11,10,1,[p1,p2],0.8)
s2 = cl.Service(17,1,13,[p1],1)
s3 = cl.Service(14,1,1,[p1,p2],0.6)
s4 = cl.Service(1,15,1,[p1],0.5)
s5 = cl.Service(12,1,1,[p1],0.7)
s6 = cl.Service(1,19,7,[p1,p2],1)
s7 = cl.Service(1,16,1,[p1],0.1)
s8 = cl.Service(11,12,10,[p1],0.3)
s9 = cl.Service(15,15,15,[p1,p2],0.4)

graph = cl.WorkFlow([(s1, s2, 0), (s2, s3, 1), (s2, s4, 1), (s4, s5, -1), (s4, s6, -1), (s5, s7, 1),(s5, s8, 1), (s6, s9, 0)],9) 


print("Price = ",graph.evaluatePrice(s1))

print("ResponseTime = ",graph.evaluateResponseTime(s1))

print("Availability = ",graph.evaluateAvailability(s1))

print("Reliability = ",graph.evaluateReliability(s1))

print("(weights equal to 1,1,1,1) \nQoS = ",graph.QoS(s1))

print("(weights equal to (price = 0.05 , response = 0.5 availability = 0.3 , reliablity = 0.15) \nQoS = ",graph.QoS(s1,[0.05,0.5,0.3,0.15]))

print("Matching = ",graph.evaluateMatching(s1))
