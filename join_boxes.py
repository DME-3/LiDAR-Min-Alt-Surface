import pickle
import numpy as np

with open('x_results.pkl','rb') as f:
    x_results = pickle.load(f)

with open('y_results.pkl','rb') as f:
    y_results = pickle.load(f)

with open('z_results.pkl','rb') as f:
    z_results = pickle.load(f)

x_array = np.array([])

for i in range(len(x_results)):
  x_array = np.concatenate((x_array, x_results[i][0]))

y_array = np.array([])

for j in range(len(y_results)):
  y_array = np.concatenate((y_array, y_results[0][j]))

lst = z_results

row=len(lst)
col=len(lst[0])

for j in range(0, row):
  print('j=%s'%(j))
  for i in range(0, col):
    print('i=%s'%(i))
    print(z_results[i][j].shape)
    if i==0:
      z_array_row = z_results[0][j]
    else:
      z_array_row = np.hstack((z_array_row, z_results[i][j]))
  
  if j==0:
    z_array = z_array_row
  else:
    z_array = np.vstack((z_array, z_array_row))
