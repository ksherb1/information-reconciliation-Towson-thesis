#!/usr/bin/env python

import os.path
import random
import numpy as np
import communication.word as word
from numbertheory.linalg import hasfullrank
from theory.multivariate import ratioofn, logofn

''' Purpose:    empirically determine how likely a random selection of points for n variables
                    will generate a solvable (non-singular) system of equations for c erased coefficients
                '''
''' Process:    1) for a given t, generate c >= t t-dimensional points to serve as an "erasure matrix" W
                3) ask if W has full rank, i.e. can it solve a system of equations?
                4) if successful, mark as success; otherwise, mark as failure and record W
                        (just so I know it's working)
                '''
''' Design:     we have 3 things to test
                
                1) How does error-rate depend on t, when c=t?
                2) How does rate of transmission c/t depend on t, for a given acceptable error-rate?
                3) Do different random bit streams have different results?
                
                Parameters:
                    
                    N(umber of trials)
                    n (width of matrix)       * experiment will test all t in [1,n]
                    RNG (random bit generator)  * must have (n,seed) constructor and next() method
                
                Output (for each (n,t,c)):  n, t, c, eps, N
                
                '''


''' simulate: n (int), t (int), c (int), R (random bit stream)
        generates W, a random n x c matrix, from R
        then selects t random columns to form Wp
        RETURN: W iff it does not have rank t
        PRE: 0 < t <= c
        '''
def simulate(n, t, c, R):
    W = np.array([R.next() for i in range(c)])
    Wp = W[:,random.sample(range(n),t)]
    if not hasfullrank(Wp):
        return Wp


''' experiment: N (int), n (int), RNG (random bit generator), out (file), [fail (file)]
        runs N experiments for all t in [1,n], c in [t,n]
        prints t, c, eps, and N for each (t,c) to out
        prints W to fail, if fail is given
        '''
def experiment(N, n, RNG, out, fail=None):
    for t in range(1,n+1):
        c = t
        
        # keep increasing c until 3 in a row are perfect
        perfects = 0
        while perfects < 3:
            eps = 0
            for i in range(N):
                # INITIALIZE RANDOM STREAM
                seed = np.array([random.randint(0,1) for j in range(n)], dtype=int)
                seed[random.choice(range(n))] |= 1    # guarantee seed has at least one 1 
                R = RNG(n, seed)
                # PROCESS SIMULATION
                W = simulate(n,t,c,R)   # None if experiment succeeded
                if W is not None:
                    eps += 1
                    if fail is not None:
                        fail.write("-----------------------------------------\n")
                        fail.write(str(W))
            eps = (1.0*eps)/N
            out.write(','.join([str(n), str(t), str(c), str(eps), str(N)])+"\n")
            # CONTROL LOOP
            if eps == 0:
                perfects +=1
            else:
                perfects = 0
            c += 1
        print "----- Finished t =",t,"experiments at c =",c,"------"

''' experiment_t: N (int), n (int), t_fun (int array->int array function),
                    RNG (random bit generator), out (file), [fail (file)]
        runs N experiments for t=tfun(n), c in [t,n]
        prints t, c, eps, and N for each (t,c) to out
        prints W to fail, if fail is given
        '''
def experiment_t(N, n, t_fun, RNG, out, fail=None):
    t = t_fun(n)
    c = t
    
    # keep increasing c until 3 in a row are perfect
    perfects = 0
    while perfects < 3:
        eps = 0
        for i in range(N):
            # INITIALIZE RANDOM STREAM
            seed = np.array([random.randint(0,1) for j in range(n)], dtype=int)
            seed[random.choice(range(n))] |= 1    # guarantee seed has at least one 1 
            R = RNG(n, seed)
            # PROCESS SIMULATION
            W = simulate(n,t,c,R)   # None if experiment succeeded
            if W is not None:
                eps += 1
                if fail is not None:
                    fail.write("-----------------------------------------\n")
                    fail.write(str(W))
        eps = (1.0*eps)/N
        out.write(','.join([str(n), str(t), str(c), str(eps), str(N)])+"\n")
        # CONTROL LOOP
        if eps == 0:
            perfects +=1
        else:
            perfects = 0
        c += 1
    print "----- Finished t =",t,"experiments at c =",c,"------"


''' start: name, [delim], [path], [ext] (all strings)
        create the file called name and give it a header, if it doesn't already exist
        RETURN an append-to file object for the given filename
        '''
def start(name, path="", ext=""):
    name = path + name + ext
    # IF FILE already exists, assume it already contains header and data
    if os.path.isfile(name):
        return open(name, "a")
    # CREATE FILE, with header
    dat = open(name, "a")
    dat.write(','.join(["N","T","C","EPS","CNT"])+"\n")
    return dat


path = "../../data/multivariate/"
ext = ".dat"
##################################################
#                 SIMULATION
##################################################
"""

NUMPY = start("NUMPY", path, ext)
LFSR = start("LFSR", path, ext)
#fail = start("FAIL", path, ext)

N = 1000
ns = [127]

for n in ns:
    print "--- Starting LFSR experiment for n =",n,"---"
    #experiment(N, n, word.LFSR, LFSR, None)
    print "--- Starting NUMPY experiment for n =",n,"---"
    experiment(N, n, word.NUMPY, NUMPY, None)
"""

##################################################
#                 TARGETING t(n)
##################################################
"""
NUMPY = start("NUMPY", path, ext)
#fail = start("FAIL", path, ext)

N = 1000
ns = range(10,510,10)
t_funs = [ratioofn(.1), ratioofn(.25), logofn(2)]

for n in ns:
    #print "--- Starting LFSR experiment for n =",n,"---"
    #experiment(N, n, word.LFSR, LFSR, None)
    print "--- Starting NUMPY experiment for n =",n,"---"
    for t_fun in t_funs:
        experiment_t(N, n, t_fun, word.NUMPY, NUMPY, None)
"""
