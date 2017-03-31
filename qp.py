'''
    File name      : qp.py
    Author         : Jinwook Jung
    Created on     : Fri Mar 31 11:04:04 2017
    Last modified  : 2017-03-31 13:08:52
    Python version : 
'''

from cvxopt import matrix, spmatrix, spdiag
from cvxopt import solvers

# A dense matrix with size of 2,3.
A = matrix([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], (2,3))   # List and dimension
B = matrix([[1.0, 2.0], [3.0, 4.0]])                # List of list

# We can create a sparse matrix from a (value, row, column) triplet.
D = spmatrix([1., 2.], [0,1], [0,1], (4,2))
print(D)

# Sparse block diagonal matrix can be created by spdiag() function
print(spdiag([B, -B, 1, 2]))


# Indexing of matrices
A = matrix(range(16), (4,4))
print (A)

# Two-argument indexing
print(A[[0,1,2,3], [0,2]])      # Row and column lists.
print(A[1,:])   # Row1
print(A[::-1, ::-1])


# Solving linear program
A = matrix([[-1.0, -1.0, 0.0, 1.0], [1.0, -1.0, -1.0, -2.0]])
b = matrix([1.0, -2.0, 0.0, 4.0])
c = matrix([2.0, 1.0])

sol = solvers.lp(c, A, b)

print(sol['x'])
