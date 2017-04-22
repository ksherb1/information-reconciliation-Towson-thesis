#!/usr/bin/env python

import numpy as np

''' STANDARD:    i identifies row, m the number of rows
                 j identifies column, n the number of columns
                 '''


# personal lightweight method designed explicitly for calculating rank of binary matrix
# 'cause I really want to beat out numpy...
# (I'm still a magnitude off...)
def hasfullrank(M):
    # FIRST, WORK WITH TALL RATHER THAN SHORT
    (m,n) = M.shape
    if m < n:
        M = np.transpose(M)
    else:
        M = np.copy(M)
    r = min(m,n)
    s = max(m,n)
    
    for j in range(r):
        # FIND THE FIRST ROW FROM I THAT HAS NONZERO ELEMENT IN COLUMN I
        i = j
        while i < s and M[i,j]==0:
            i += 1
        # IF LOOP WENT ALL THE WAY THROUGH, COLUMN ONLY HAS ZEROS: |M|=0
        if i == s:
            return False
        # IF LOOP DID ANYTHING AT ALL, WE MUST PERMUTE
        if i > j:
            M[j,:], M[i,:] = M[i,:].copy(), M[j,:].copy()
        # ROW I IS NOW READY FOR REDUCTION
        for i in range(j+1,m):
            if M[i,j] == 1:
                for k in range(j,r):
                    M[i,k] ^= M[j,k]
    return True




''' solve: A (2D matrix), B (2D matrix)
        finds a solution to A*x=B,
            where A is a coefficient matrix and B a vector
        # of unknowns 'n' is the # of columns in A
            If rank of A turns out to be less than # of unknowns,
            and therefore no solution exists, return None
        PRE: B must have 1 column and same # of rows as A
             A and B must be in same field
        '''
def solve(A, B):
    if not (B.m == A.m):
        raise ValueError("A and B have incompatible sizes.")
    if not (B.n == 1):
        raise ValueError("B has too many columns.")
    if not (B.F == A.F):
        raise ValueError("A and B have incompatible elements.")
    if A.m < A.n:   # IF COLUMNS OUTNUMBER ROWS, OBVIOUSLY NO SOLUTION
        return None
    
    AUG = Matrix(np.concatenate((A.M, B.M), axis=1), A.F)
    
    for i in range(A.n):    # we don't need to reduce last column in AUG
        # FIND THE FIRST ROW FROM I THAT HAS NONZERO ELEMENT IN COLUMN I
        ii = i
        while ii < AUG.m and AUG[ii,i]==AUG.F.zero:
            ii += 1
        # IF LOOP WENT ALL THE WAY THROUGH, COLUMN ONLY HAS ZEROS: no solution
        if ii == AUG.m:
            return None
        # OTHERWISE, IF LOOP DID ANYTHING AT ALL, WE MUST PERMUTE
        if ii > i:
            AUG.M[i,:], AUG.M[ii,:] = AUG.M[ii,:].copy(), AUG.M[i,:].copy()
        # ROW I IS NOW READY FOR REDUCTION
        AUG = AUG.reduce(i)
    
    # at this point, the top-left n x n sub-matrix of AUG is diagonal
    # we can easily solve each equation with a simple inverse and multiplication
    x = np.zeros(A.n, dtype=B.M.dtype)
    for i in range(A.n):
        x[i] = AUG.F[AUG.F.inv(AUG[i,i]) * AUG[i,A.n]]
    
    # check for contradictions
    if A.m > A.n and not AUG[A.n, A.n] == AUG.F.zero:
        return None
    
    return x




''' Matrix: implementation for matrices whose elements exist in a finite field '''
class Matrix:
    ''' Matrix: M (1 or 2d-array) F (FiniteField)
            all elements of M must be in F
            '''
    def __init__(self, M, F):
        if np.ndim(M) < 2:
            M = np.reshape(M, (1,len(M)))
            
        (m, n) = M.shape
        '''
        for i in range(m):
            for j in range(n):
                if M[i,j] not in F:
                    raise ValueError("M contains elements not in "+str(F))
        '''
        self.m = m
        self.n = n
        self.M = M
        self.F = F
    
    # MAGIC CONTAINER METHODS
    ''' len is not supported '''
        
    ''' Matrix[key] just wraps [key] of M array in a Matrix,
            or returns it if it's atomic
            '''
    def __getitem__(self, key):
        val = self.M[key]
        if isinstance(val, np.ndarray):
            if np.ndim(val) < 2:    # ensure constructor still gets 2D array
                val = np.reshape(val, (1,len(val)))
            return Matrix(val, self.F)
        return val  # atomic case
    
    # MISCELLANEOUS MAGIC METHODS
    ''' str(Matrix) reports FiniteField and then just gives normal numpy strification '''
    def __str__(self):
        return "Elements in "+str(self.F)+":\n"+str(self.M)
    
    ''' M1 == M2 iff they have the same shape and all elements 'equal' one another '''
    def __eq__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError("Cannot compare matrix to "+str(other))
        if self.F == other.F and self.m == other.m and self.n == other.n:
            for i in range(self.m):
                for j in range(self.n):     # note comparison is in field, not by value
                    if not self.F[self[i,j]] == self.F[other[i,j]]:
                        return False        # found a non-matching element
            return True                     # everything matched
        return False                        # field or shape did not match
    ''' other comparisons are not supported '''
    
    # MATRIX ARITHMETIC
    # -- UNARY OPERATORS --
    ''' -Matrix is just the matrix with each element additively inversed in F '''
    def __neg__(self):
        X = np.copy(self.M)     # create new array we will make edits to
        for i in range(self.m):
            for j in range(self.n):
                X[i,j] = self.F.neg(X[i,j])
        return Matrix(X, self.F)
    
    # --- BINARY OPERATORS ---
    ''' M1 + M2 adds each element piecewise, if they are compatible '''
    def __add__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError("Cannot add "+str(other)+" to a Matrix")
        if not self.F == other.F:
            raise ValueError("Matrix arguments have different coefficient fields. Cannot add.")
        if not (self.m == other.m and self.n == other.n):
            raise ValueError("Matrix dimensions do not match. Cannot add.")
        
        X = np.copy(self.M)     # create new array we will make edits to
        for i in range(self.m):
            for j in range(self.n):
                # addition automatically coerces result to standard residue in field
                X[i,j] = self.F[X[i,j] + other[i,j]]
        return Matrix(X, self.F) 
    
    ''' M1 - M2 is, naturally, M1 + -M2 '''
    def __sub__(self, other):
        return self + -other
    
    ''' M1 * M2 is matrix multiplication - not element-wise!
            Unless, of course, M2 is a scalar '''
    def __mul__(self, other):
        # if other is a member of F, it's a scalar: multiply element-wise
        if other in self.F:
            X = np.copy(self.M)
            for i in range(self.m):
                for j in range(self.n):
                    X[i,j] = self.F[X[i,j] * other]
        
        if not isinstance(other, Matrix):
            raise TypeError("Cannot multiply "+str(other)+" by a Matrix")
        if not self.F == other.F:
            raise ValueError("Matrix arguments have different coefficient fields. Cannot multiply.")
        if not self.n == other.m:
            raise ValueError("Inner dimensions do not match. Cannot multiply.")
        
        X = np.zeros((self.m, other.n), dtype=self.M.dtype) # initialize new array
        for i in range(self.m):
            for j in range(other.n):
                for k in range(self.n):
                    # multiplication automatically coerces result to standard residue in field
                    X[i,j] = self.F[self[i,k]*other[k,j] + X[i,j]]
        return Matrix(X, self.F)
    
    ''' reciprocal multiplication to catch (scalar * matrix) operations '''
    def __rmul__(self, other):
        return self * other
    
    # OTHER METHODS
    
    ''' T: returns the transpose of this matrix '''
    def T(self):
        X = np.transpose(self.M)
        return Matrix(X, self.F)
    
    ''' omit: i (int), j (int)
            returns the matrix with row i and column j omitted
            PRE: i must be a valid row, j a column
            '''
    def omit(self, i, j):
        if not (0 <= i and i < self.m):
            raise ValueError("Invalid i: must be a row index")
        if not (0 <= j and j < self.n):
            raise ValueError("Invalid j: must be a column index")
        
        M = np.delete(self.M, i, axis=0)    # omit row
        M = np.delete(M, j, axis=1)         # omit column
        return Matrix(M, self.F)
    
    ''' rank: returns the rank of the matrix
            '''
    def rank(self):
        R = Matrix(np.copy(self.M), self.F)
        if R.m < R.n:   # ALGORITHM IS SIMPLER IF MATRIX IS TALL...
            R = R.T()
        r = R.n         # ASSUME RANK IS FULL UNTIL PROVEN OTHERWISE
        
        for i in range(r):  # r may change, but generator is made just once
            # FIND THE FIRST ROW FROM I THAT HAS NONZERO ELEMENT IN COLUMN I
            ii = i
            while ii < self.m and R[ii,i]==self.F.zero:
                ii += 1
            # IF LOOP WENT ALL THE WAY THROUGH, COLUMN ONLY HAS ZEROS: r -= 1
            if ii == self.m:
                r -= 1
                continue
            # OTHERWISE, IF LOOP DID ANYTHING AT ALL, WE MUST PERMUTE
            if ii > i:
                R.M[i,:], R.M[ii,:] = R.M[ii,:].copy(), R.M[i,:].copy()
            # ROW I IS NOW READY FOR REDUCTION
            R = R.reduce(i)
        return r
    
    ''' reduce: i (int)
            returns the matrix with column i reduced to zero except at row i
                if M[i,i] is 0 (and thus cannot be reduced), returns a copy of itself
            PRE: 0 <= i < min(self.n, self.m)
            '''
    def reduce(self, i):
        if not (0 <= i and i < min(self.n, self.m)):
            raise ValueError("Invalid index to reduce on.")
        
        X = np.copy(self.M)
        
        if self[i,i] == self.F.zero:
            return Matrix(X, self.F)      # this row can't be reduced
        
        # STEP ONE: GET THE NORM OF THE ROW TO REDUCE BY
        norm = self.F.inv(X[i,i])
        
        for ii in range(self.m):
            if i != ii: # no reduction needed on the reducing row
                # STEP TWO: GET THE SCALE OF THE ROW TO REDUCE
                scale = X[ii,i]
                for j in range(self.n):
                    X[ii,j] = self.F[ X[ii,j] - (norm*scale*X[i,j]) ]
        return Matrix(X, self.F)
    
    
    
    
    ### METHODS FOR SQUARE MATRICES
    ''' det:
            returns the determinant of the matrix
            PRE: self is square
            '''
    def det(self):
        if not (self.m == self.n):
            raise ValueError("Determinant invalid for non-square matrix")
        
        # EASY CASE: SELF IS ATOMIC
        if self.m == 1:
            return self.M[0,0]
        
        # STEP ONE: REDUCE TO A DIAGONAL MATRIX, PERMUTING ROWS AS NEEDED
        R = Matrix(np.copy(self.M), self.F)
        
        swaps = 0       # tracks number of swaps for negation step
        for i in range(self.m):
            # FIND THE FIRST ROW FROM I THAT HAS NONZERO ELEMENT IN COLUMN I
            ii = i
            while ii < self.m and R[ii,i]==self.F.zero:
                ii += 1
            # IF LOOP WENT ALL THE WAY THROUGH, COLUMN ONLY HAS ZEROS: |M|=0
            if ii == self.m:
                return self.F.zero
            # IF LOOP DID ANYTHING AT ALL, WE MUST PERMUTE
            if ii > i:
                R.M[i,:], R.M[ii,:] = R.M[ii,:].copy(), R.M[i,:].copy()
                swaps += 1
            # ROW I IS NOW READY FOR REDUCTION
            R = R.reduce(i)
        
        # STEP TWO: MULTIPLY ALONG THE DIAGONAL
        D = self.F.one
        for i in range(self.m):
            D = self.F[R[i,i] * D]
        # ACCOUNT FOR PERMUTATIONS
        if swaps & 1:
            D = self.F[-D]
        
        return D
        
    
    ''' slow_det:
            returns the determinant of the matrix
            using O(N!) recursive algorithm...
            PRE: self is square
            '''
    def slow_det(self):
        if not (self.m == self.n):
            raise ValueError("Determinant invalid for non-square matrix")
        
        # base case: self is atomic
        if self.m == 1:
            return self[0,0]
        # recursive case: multiply each element of the first row by its cofactor, and add
        D = self.F.zero
        for j in range(self.n):
            D = self.F[self[0,j]*self.cofactor(0,j) + D]
        return D
    
    ''' minor: i (int), j (int)
            returns the minor of element (i,j)
            which is the determinant of the matrix with row i and column j omitted
            PRE: self is square
            '''
    def minor(self, i, j):
        if not (self.m == self.n):
            raise ValueError("Minor invalid for non-square matrix")
        return self.omit(i,j).det()
    
    ''' cofactor: i (int), j (int)
            returns cofactor of element (i,j)
                which is minor of (i,j), times negative one if i+j is odd
            OR, if i == j == None, returns cofactor of matrix
                which is matrix of cofactors for each (i,j)
            PRE: self is square
            '''
    def cofactor(self, i=None, j=None):
        if not (self.m == self.n):
            raise ValueError("Cofactor invalid for non-square matrix")
        if not ((i is None) == (j is None)):
            raise ValueError("i and j must both or neither be None")
        if i is not None:
            # base case: return minor, times negative one if i+j is odd
            return -self.minor(i,j) if (i+j)&1 else self.minor(i,j)
        
        # recursive case: return matrix of each minor 
        M = np.zeros(self.M.shape, dtype=self.M.dtype)
        for i in range(self.m):
            for j in range(self.n):
                M[i,j] = self.cofactor(i,j)
        return Matrix(M, self.F)
    
    ''' inverse:
            returns inverse of matrix using Cramer's rule
            PRE: self is square
            '''
    def inverse(self):
        if not (self.m == self.n):
            raise ValueError("Inverse invalid for non-square matrix")
        return self.F.inv(self.det()) * self.cofactor()
