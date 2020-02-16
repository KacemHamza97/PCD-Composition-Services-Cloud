import numpy as np
from sklearn.linear_model import LinearRegression
import pickle
import csv
# regression dataset
X,Y = [] , []
with open('dataset.csv', mode = 'r') as file:
     reader = csv.DictReader(file)
     for test_value in reader:
         X.append([test_value['activities'],test_value['candidates'],test_value['fitness_normalized'],test_value['scalability']])
         Y.append([test_value['MCN'],test_value['SQ'],test_value['SN']])

X, Y = np.array(X).astype(np.float64).reshape(-1,4) , np.array(Y).astype(np.float64)
# fit final model
model = LinearRegression()
model.fit(X, Y)
# Saving model
with open("model.pkl", 'wb') as file:
    pickle.dump(model, file)
