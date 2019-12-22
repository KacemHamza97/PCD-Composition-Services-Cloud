import cloud

p1 = cloud.Product(12,30)
p2 = cloud.Product(5,50)

s1 = cloud.Service(1,11,10,1,[p1,p2],0.8)
s2 = cloud.Service(2,17,1,13,[p1],1)
s3 = cloud.Service(3,14,1,1,[p1,p2],0.6)
s4 = cloud.Service(4,1,15,1,[p1],0.5)
s5 = cloud.Service(5,12,1,1,[p1],0.7)
s6 = cloud.Service(6,1,19,7,[p1,p2],1)
s7 = cloud.Service(7,1,16,1,[p1],0.1)
s8 = cloud.Service(8,11,12,10,[p1],0.3)
s9 = cloud.Service(9,15,15,15,[p1,p2],0.4)
s10= cloud.Service(8,15,15,15,[p1,p2],0.4)

compo = cloud.WorkFlow(s1,[(s1, s2, 0), (s2, s3, 1), (s2, s4, 1), (s4, s5, -1), (s4, s6, -1), (s5, s7, 1),(s5, s8, 1), (s6, s9, 0)]) 

compo.mutate(s8,s10)

print("Euclidean Distance between s1 and s2 = ",s1.euclideanDist(s2))

print("Price = ",compo.evaluatePrice())

print("ResponseTime = ",compo.evaluateResponseTime())

print("Availability = ",compo.evaluateAvailability())

print("Reliability = ",compo.evaluateReliability())

print("(weights equal to 1,1,1,1) \nQoS = ",compo.QoS())

print("(weights equal to (price=0.05,response=0.5,availability=0.3,reliablity=0.15) \nQoS = ",compo.QoS([0.05,0.5,0.3,0.15]))

print("Matching = ",compo.evaluateMatching(s1))

compo.crossover(compo)


