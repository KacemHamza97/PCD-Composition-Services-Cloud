import cloud
import hybrid

p1 = cloud.Product(12,30)
p2 = cloud.Product(5,50)

s1 = cloud.Service(1,11,10,1,[p1],0.8)
s2 = cloud.Service(2,17,1,13,[p1],1)
s3 = cloud.Service(3,14,1,1,[p1,p2],0.6)
s4 = cloud.Service(4,1,15,1,[p1],0.5)
s5 = cloud.Service(5,12,1,1,[p1],0.7)
s6 = cloud.Service(6,1,19,7,[p1],1)
s7 = cloud.Service(7,1,16,1,[p1],0.1)
s8 = cloud.Service(8,11,12,10,[p1],0.3)
s9 = cloud.Service(9,15,15,15,[p1,p2],0.4)

s11 = cloud.Service(1,6,10,1,[p1,p2],0.8)
s21 = cloud.Service(2,26,1,13,[p1],1)
s31 = cloud.Service(3,4,6,1,[p2],0.6)
s41 = cloud.Service(4,11,15,1,[p1],0.5)
s51 = cloud.Service(5,15,6,1,[p1],0.7)
s61 = cloud.Service(6,3,19,7,[p1,p2],1)
s71 = cloud.Service(7,6,16,1,[p1],0.1)
s81 = cloud.Service(8,4,12,10,[p1],0.3)
s91 = cloud.Service(9,1,15,15,[p2],0.4)

s12 = cloud.Service(1,8,10,1,[p1,p2],0.8)
s22 = cloud.Service(2,20,1,13,[p1],1)
s32 = cloud.Service(3,12,1,1,[p1,p2],0.6)
s42 = cloud.Service(4,3,15,1,[p1],0.5)
s52 = cloud.Service(5,14,1,1,[p1],0.7)
s62 = cloud.Service(6,15,19,7,[p2],1)
s72 = cloud.Service(7,7,16,1,[p1],0.1)
s82 = cloud.Service(8,1,12,10,[p1],0.3)
s92 = cloud.Service(9,5,15,15,[p1,p2],0.4)

s13 = cloud.Service(1,4,11,11,[p1,p2],0.8)
s23 = cloud.Service(2,10,13,3,[p1],1)
s33 = cloud.Service(3,2,8,12,[p2],0.6)
s43 = cloud.Service(4,13,5,18,[p1],0.5)
s53 = cloud.Service(5,4,7,11,[p1],0.7)
s63 = cloud.Service(6,5,9,7,[p1,p2],1)
s73 = cloud.Service(7,17,6,1,[p1],0.1)
s83 = cloud.Service(8,11,2,1,[p1],0.3)
s93 = cloud.Service(9,15,5,5,[p1,p2],0.4)

s14 = cloud.Service(1,21,10,1,[p1,p2],0.8)
s24 = cloud.Service(2,12,11,3,[p1],1)
s34 = cloud.Service(3,15,3,11,[p1,p2],0.6)
s44 = cloud.Service(4,23,5,10,[p1],0.5)
s54 = cloud.Service(5,24,1,14,[p1],0.7)
s64 = cloud.Service(6,5,1,17,[p1],1)
s74 = cloud.Service(7,7,1,5,[p1],0.1)
s84 = cloud.Service(8,21,2,1,[p1],0.3)
s94 = cloud.Service(9,15,5,1,[p1],0.4)

services = [[s1,s11,s12,s13,s14],[s2,s21,s22,s23,s24],[s3,s31,s32,s33,s34],[s4,s41,s42,s43,s44],[s5,s51,s52,s53,s54],[s6,s61,s62,s63,s64],[s7,s71,s72,s73,s74],[s8,s81,s82,s83,s84],[s9,s91,s92,s93,s94]]


actGraph = [[1, 2, 0], [2, 3, 1], [2, 4, 1], [4, 5, -1], [4, 6, -1], [5, 7, 1],[5, 8, 1], [6, 9, 0]]

rootAct = 1
print("Best solution is ", hybrid.ABCgenetic(rootAct,actGraph,services,5,60,50,0.3))
