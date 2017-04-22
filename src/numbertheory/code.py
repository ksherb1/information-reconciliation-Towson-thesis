#!/usr/bin/env python

import numpy as np

from field import FiniteField as GF
from linalg import Matrix

''' RS: q (int or FiniteField), t (int)
        returns parity-check matrix of an RS code 
            which is a (q-1) by t matrix,
            where each element (i,j) is alpha^ij,
            where alpha is a generator of GF(q)
        '''
def RS(q, shape):
    if isinstance(q, GF):
        F = q
        q = F.order
    else:
        F = GF(q)
    a = F.alpha()
    
    (t,n) = shape
    
    H = np.full((t,n), F.one, dtype=type(F.one))
    
    # STEP ONE - FILL THE FIRST ROW: H_0j = a**j
    for j in range(1, n):
        H[0,j] = F[a*H[0,j-1]]
    
    # STEP TWO - FILL THE REST
    for j in range(1, n):
        apow = H[0,j]
        for i in range(1,t):
            H[i,j] = F[apow*H[i-1,j]]
    
    return Matrix(H,F)