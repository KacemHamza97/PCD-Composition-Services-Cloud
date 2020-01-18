import pickle
from numpy import array

with open("model.pkl", 'rb') as file:
    model = pickle.load(file)

# input
x1 = int(input("NUMBER OF ACTIVITIES : "))
x2 = int(input("NUMBER OF CANDIDATE SERVICES : "))
Xnew = array([x1,x2,1,0]).reshape(-1,4)

# predict
Ynew = model.predict(Xnew)
print("RECOMMENDED : ")
print("Iterations = {}\nScouts condition = {}\nFood Sources = {}\n".format(int(Ynew[0][0]),int(Ynew[0][1]),int(Ynew[0][2])))
