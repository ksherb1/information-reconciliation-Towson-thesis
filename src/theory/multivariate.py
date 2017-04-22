from scipy.optimize import fsolve
import numpy as np
from math import log


''' factories to create functions producing t from n '''
ratioofn = lambda p: lambda n: np.ceil(p*n).astype(int)
logofn = lambda b: lambda n: np.ceil(np.log(n)/np.log(b)).astype(int)

''' P - probability that c n-vectors have full rank '''
def P(n,c=None):
    if c is None:
        c = n
    P = 1.0
    for k in range(n):
        P *= _p(k,c)
    return P

''' p - probability that a random n-vector is not in the span of a rank k matrix '''
def _p(k, n):
    return 1 - 2**-(n-k)

''' E - probability that t by d+t matrix has rank less than t
        first-order approximation except at d=0: not very accurate for d=1 and 2 '''
def E(t,d):
    if d == 0:           # small order correction, when approximation is no good
        return 1-P(t)
    return (2**-d) * (1-2**-t)

''' D - effective excess communication complexity from probabilistic protocol with c=d+t '''
def D(t,d):
    if d == 0:
        return t*(2**t-1)
    return (d + 2**-d * (t*(1-2**-t))) / (1 - 2**-d * (1-2**-t))

''' d_min - d which minimizes D(t,d)
        numerical solution using scipy.fsolve '''
def d_min(t):
    if t == 0:      # if no error, no communication needed
        return 0    # so definitely no excess needed
    dD = lambda d: 1 - (1-2**-t)*2**-d * (1 + t*log(2) + d)
    return fsolve(dD, log(t,2))[0]