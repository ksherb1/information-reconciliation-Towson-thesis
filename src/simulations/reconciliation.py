import numpy as np
import time
import os

import communication.word as word
import communication.channel as channel

from numbertheory.field import FiniteField as GF
from numbertheory.code import RS
from numbertheory.linalg import Matrix, solve

from theory.multivariate import D as excess
from theory.multivariate import ratioofn, logofn

''' Purpose:    compare run-time efficiency between implemented reconciliation protocols
                '''
''' Process:    1) generate a random x
                2) pass x through an erasure channel to form y
                3) calculate RS s and perform reconciliation
                4) calculate RN s and perform reconciliation
                '''
''' Design:     we would like to further compare RS and RN protocols
                
                to fairly compare, m=2 and we use binary RS adaptation
                select c for RN protocol according to min d
                
                do steps 1-4 many times and collect time data to plot
                '''
Z2 = GF(2)      # binary finite field for polynomial coefficients

''' nonbinary protocol, adapted to binary '''
def simulate_RS(x0, y0, m, H, F):
    # ZEROTH pad x0 with zeros so its length is divisible by m
    xp = x0
    if len(x0) % m != 0:
        xp = np.pad(x0, (0,m-len(x0)%m), 'constant')
    
    # FIRST convert x and y into polynomial arrays
    x = word.polynomials(xp, Z2, m)
    y = np.copy(x)
    for i in range(len(x0)):     # erase each polynomial containing an erasure
        if y0[i] < 0:
            y[i/m] = None
    
    # SECOND solve the erasures
    s = H * Matrix(x,F).T()                                 # calculate redundancy
    X = np.array([F.zero if i is None else i for i in y])   # pretend erasures are 0
    z = s - H * Matrix(X,F).T()                             # get right-hand side of equation
    locs = np.where([i==None for i in y])[0]                # find error locations
    h = H[:,locs]                                           # get left-hand side of equation
    e = solve(h, z)                                         # solve for our error
    X[locs] = e                                             # add in our error
    
    # THIRD convert result into bits
    X0 = np.zeros(len(xp), dtype=int)
    for i in range(len(X)):
        sec = X[i].array()
        sec = np.pad(sec, (0,m-len(sec)), 'constant')
        X0[m*i:m*(i+1)] = sec
    
    if len(X0) > len(x0):
        X0 = X0[:len(x0)-len(X0)]                           # trim off any extra zeros
    return X0

''' probabilistic simulation '''
def simulate_RN(x, y, c, R):
    H = np.array([R.next() for i in range(c)])              # generate H
    H = Matrix(H, Z2)
    
    s = H * Matrix(x,Z2).T()                                # calculate redundancy
    X = np.array([0 if i < 0 else i for i in y])            # pretend erasures are 0
    S = s - H * Matrix(X,Z2).T()                            # get right-hand side of equation
    locs = np.where([i<0 for i in y])[0]                    # find error locations
    h = H[:,locs]                                           # get left-hand side of equation
    e = solve(h, S)                                         # solve for our error
    if e is None:
        X = y
    else:
        X[locs] = e                                         # add in our error
    
    return X

''' collect data '''
def experiment(n, t, N):
    # CONSTRUCT the list of x's
    xs = [word.random(n) for i in range(N)]
    # CONSTRUCT the list of y's
    ys = [channel.erasure(x,t=t) for x in xs]
    
    # PICK H for RS reconciliation
    #     note that RS has advantage of not needing to recreate H each time
    m = 1
    while n > m*(2**m - 1):
        m += 1
    
    F = GF(2**m)
    nP = int(np.ceil((1.0*n)/m))  # number of polynomials in x
    H = RS(F, (t, nP))
    
    # PICK R for RN reconciliation
    R = word.NUMPY(n, word.random(n))
    
    # PICK c for RN reconciliatiion
    d = -1
    Dp = excess(t,d+1)
    D = Dp + 1      # just whatever it must to get the loop to run
    while Dp < D:
        d += 1
        D = Dp
        Dp = excess(t,d+1)
    c = d+t 
    
    # IMPLEMENT the protocol for RS reconciliation
    now = time.time()
    err_RS = 0
    for i in range(N):
        X = simulate_RS(xs[i], ys[i], m, H, F)
        if not all(xs[i]==X):
            err_RS += 1.0/N
    time_RS = time.time() - now
    
    # IMPLEMENT the protocol for RS reconciliation
    now = time.time()
    err_RN = 0
    for i in range(N):
        X = simulate_RN(xs[i], ys[i], c, R)
        if not all(xs[i]==X):
            err_RN += 1.0/N
    time_RN = time.time() - now
    
    return time_RS, err_RS, time_RN, err_RN

''' output data '''
def write(data, out):
    strs = [str(datum) for datum in data]
    out.write(','.join(strs)+"\n")
    out.flush()

''' load file '''
def start(name, path="", ext=""):
    name = path + name + ext
    # IF FILE already exists, assume it already contains header and data
    if os.path.isfile(name):
        return open(name, "a")
    # CREATE FILE, with header
    dat = open(name, "a")
    dat.write(','.join(["N","T","CNT","RS_TIME","RS_ERR","RN_TIME","RN_ERR"])+"\n")
    dat.flush()
    return dat

######################
# MAIN SCRIPT
######################
path = "../../data/reconciliation/"
ext = ".dat"

tenth = start("tenth", path, ext)
quarter = start("quarter", path, ext)
log2 = start("log2", path, ext)


N = 10
#ns = [10]
ns = range(2,10)
#t_funs = [ratioofn(.1), ratioofn(.25), logofn(2)]

for n in ns:
    # t = n/10
    t = ratioofn(.1)(n)
    time_RS, err_RS, time_RN, err_RN = experiment(n, t, N)
    write((n,t,N,time_RS,err_RS,time_RN,err_RN), tenth)
    # t = n/4
    t = ratioofn(.25)(n)
    time_RS, err_RS, time_RN, err_RN = experiment(n, t, N)
    write((n,t,N,time_RS,err_RS,time_RN,err_RN), quarter)
    # t = log_2 n
    t = logofn(2)(n)
    time_RS, err_RS, time_RN, err_RN = experiment(n, t, N)
    write((n,t,N,time_RS,err_RS,time_RN,err_RN), log2)
    
    print "Finished simulation for n =",n
    

