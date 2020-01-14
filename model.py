from numpy import array
from sklearn.linear_model import LinearRegression
# regression dataset
print("DATASET NOT COMPLETELY BUILT : JUST A FEW RANDOM SAMPLES ...")
X, Y = array([[5,50,0.93],[10,100,0.4],[10,100,0.99],[20,150,0.87],[20,150,0.79],[30,200,0.91],[30,200,0.89]]).reshape(-1,3) , array([[100,10,100],[200,12,200],[218,13,250],[400,15,250],[380,13,300],[500,18,350],[500,17,400]])
# fit final model
model = LinearRegression()
model.fit(X, Y)
# new
x1 = int(input("NUMBER OF ACTIVITIES : "))
x2 = int(input("NUMBER OF CANDIDATE SERVICES : "))
Xnew = array([n1,n2,1]).reshape(-1,3)
# predict
Ynew = model.predict(Xnew)
print("RECOMMENDED : ")
print("Iterations = {}\nScouts condition = {}\nFood Sources = {}\n".format(int(ynew[0][0]),int(ynew[0][1]),int(ynew[0][2])))
