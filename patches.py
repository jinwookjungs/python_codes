'''
    File name      : patches.py
    Author         : Jinwook Jung
    Created on     : Fri Mar 31 14:13:26 2017
    Last modified  : 2017-03-31 14:13:26
    Python version : 
'''

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.pyplot import Rectangle
from matplotlib.collections import PatchCollection
from time import gmtime, strftime

# Diamond 1
verts1 = [(-3,0), (0,-3), (3,0), (0,3), (-3,0)]
codes1 = [Path.MOVETO, Path.LINETO, Path. LINETO, Path.LINETO, Path.CLOSEPOLY]
path1 = Path(verts1, codes1)
patch1 = patches.PathPatch(path1, lw=2, alpha=0.2)

# Diamond 2
verts2 = [(1,0), (4,-3), (7,0), (4,3), (1,0)]
codes2 = [Path.MOVETO, Path.LINETO, Path. LINETO, Path.LINETO, Path.CLOSEPOLY]
path2 = Path(verts2, codes2)
patch2 = patches.PathPatch(path2, lw=2, alpha=0.2)

# Diamond 3 - Source
verts3 = [(-7,9), (2,0), (11,9), (2,18), (-7,9)]
codes3 = [Path.MOVETO, Path.LINETO, Path. LINETO, Path.LINETO, Path.CLOSEPOLY]
path3 = Path(verts3, codes3)
patch3 = patches.PathPatch(path3, lw=2, alpha=0.2)

# Diamond 4
verts4 = [(-1,2), (2,-1), (5,2), (2,5), (-1,2)]
codes4 = [Path.MOVETO, Path.LINETO, Path. LINETO, Path.LINETO, Path.CLOSEPOLY]
path4 = Path(verts4, codes4)
patch4 = patches.PathPatch(path4, lw=2, alpha=0.2)

# LP
# Minimize
from cvxopt import matrix, solvers
# x_1, y_1, x_2, y_2, x_3, y_3, x_4, y_4, x, y
c = matrix( [ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  0.,  0.])
A = matrix([[-1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.],     # x_1
            [-1.,  0.,  0.,  0.,  0.,  0.,  0.,  0., -1.,  0.], 
            [ 0., -1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.],     # y_1
            [ 0., -1.,  0.,  0.,  0.,  0.,  0.,  0.,  0., -1.], 
            [ 0.,  0., -1.,  0.,  0.,  0.,  0.,  0.,  1.,  0.],     # x_2
            [ 0.,  0., -1.,  0.,  0.,  0.,  0.,  0., -1.,  0.], 
            [ 0.,  0.,  0., -1.,  0.,  0.,  0.,  0.,  0.,  1.],     # y_2
            [ 0.,  0.,  0., -1.,  0.,  0.,  0.,  0.,  0., -1.], 
            [ 0.,  0.,  0.,  0., -1.,  0.,  0.,  0.,  1.,  0.],     # x_3
            [ 0.,  0.,  0.,  0., -1.,  0.,  0.,  0., -1.,  0.], 
            [ 0.,  0.,  0.,  0.,  0., -1.,  0.,  0.,  0.,  1.],     # y_3
            [ 0.,  0.,  0.,  0.,  0., -1.,  0.,  0.,  0., -1.], 
            [ 0.,  0.,  0.,  0.,  0.,  0., -1.,  0.,  1.,  0.],     # x_4
            [ 0.,  0.,  0.,  0.,  0.,  0., -1.,  0., -1.,  0.], 
            [ 0.,  0.,  0.,  0.,  0.,  0.,  0., -1.,  0.,  1.],     # y_4
            [ 0.,  0.,  0.,  0.,  0.,  0.,  0., -1.,  0.,  -1.]])
#            [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  1.],     # MR Boundary
#            [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1., -1.], 
#            [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0., -1., -1.], 
#            [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0., -1.,  1.]])
b = matrix([2., -2., 9., -9., 
            0., 0., 0., 0., 
            4., -4., 0., 0., 
            2., -2., 0., 0.])
#            3., 2., -1., -1.])

sol =solvers.lp(c, A.trans(), b)
print(sol['x'])
print(sol['x'][-2:])

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal')
ax.scatter(sol['x'][-2], sol['x'][-1])
ax.add_patch(patch1)
ax.add_patch(patch2)
ax.add_patch(patch3)
ax.add_patch(patch4)
ax.set_xlim(-5,10)
ax.set_ylim(-5,10)


plt.show()
