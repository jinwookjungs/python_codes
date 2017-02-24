'''
    File name      : colorize.py
    Author         : Jinwook Jung
    Created on     : Fri Feb 24 01:17:43 2017
    Last modified  : 2017-02-24 01:21:34
    Python version : 
'''

import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import numpy as np

N = 100     # Number of rectangles
x_list = np.random.random(N)
y_list = np.random.random(N)
w_list = 0.1*np.random.random(N)
h_list = 0.1*np.random.random(N)
patches = []

x_list = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
y_list = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
w_list = [0.1]*10
h_list = [0.1]*10

for x,y,w,h in zip(x_list, y_list, w_list, h_list):
    rectangle = Rectangle((x,y), w, h)
    patches.append(rectangle)

fig = plt.figure()
ax = fig.add_subplot(111)

col = PatchCollection(patches, cmap=cm.jet, alpha=0.4)
col.set(array=np.array(x_list), cmap='jet')
ax.add_collection(col)
plt.colorbar(col)

plt.show()
