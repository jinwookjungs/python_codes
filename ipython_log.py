# IPython log file

get_ipython().magic('logstart')
import numpy as np
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
rect = plt.Rectangle((0.2,0.75), 0.4, 0.15, color='k', alpha=0.3)
ax.add_patch(rect)
exit()
