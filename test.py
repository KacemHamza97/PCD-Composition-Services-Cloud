import cloud
import hybrid

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

s11 = cloud.Service(1,6,10,1,[p1,p2],0.8)
s21 = cloud.Service(2,26,1,13,[p1],1)
s31 = cloud.Service(3,4,1,1,[p1,p2],0.6)
s41 = cloud.Service(4,11,15,1,[p1],0.5)
s51 = cloud.Service(5,15,1,1,[p1],0.7)
s61 = cloud.Service(6,3,19,7,[p1,p2],1)
s71 = cloud.Service(7,6,16,1,[p1],0.1)
s81 = cloud.Service(8,4,12,10,[p1],0.3)
s91 = cloud.Service(9,1,15,15,[p1,p2],0.4)

s12 = cloud.Service(1,8,10,1,[p1,p2],0.8)
s22 = cloud.Service(2,20,1,13,[p1],1)
s32 = cloud.Service(3,12,1,1,[p1,p2],0.6)
s42 = cloud.Service(4,3,15,1,[p1],0.5)
s52 = cloud.Service(5,14,1,1,[p1],0.7)
s62 = cloud.Service(6,15,19,7,[p1,p2],1)
s72 = cloud.Service(7,7,16,1,[p1],0.1)
s82 = cloud.Service(8,1,12,10,[p1],0.3)
s92 = cloud.Service(9,5,15,15,[p1,p2],0.4)

services = [[s1,s11,s12],[s2,s21,s22],[s3,s31,s32],[s4,s41,s42],[s5,s51,s52],[s6,s61,s62],[s7,s71,s72],[s8,s81,s82],[s9,s91,s92]]


actGraph = [[1, 2, 0], [2, 3, 1], [2, 4, 1], [4, 5, -1], [4, 6, -1], [5, 7, 1],[5, 8, 1], [6, 9, 0]]

rootAct = 1

print("Best solution is ",hybrid.ABCgenetic(rootAct,actGraph,services,3,100,3,0.3).QoS())


