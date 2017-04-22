#!/usr/bin/env python


import numpy as np
import random
from flask import Flask, render_template, request, jsonify

import communication.word as word
import communication.channel as channel

from numbertheory.field import FiniteField as GF
from numbertheory.code import RS
from numbertheory.linalg import Matrix, solve

from theory.multivariate import D as excess


app = Flask(__name__,
        static_folder="../static",
        template_folder="../templates"
        )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/erasure/rs')
def erasure_rs():
    return render_template('erasure/rs.html')

@app.route('/erasure/rn')
def erasure_rn():
    return render_template('erasure/rn.html')

@app.route('/erasure/rs/simulate', methods=['POST'])
def erasure_rs_simulate():
    input = request.get_json()
    
    # PROCESS INPUT
    m = input['m']
    n = input['n']
    t = input['t']
    if 'seed' in input:
        np.random.seed(input['seed'])
        random.seed(input['seed'])
        
    
    q = 2**m
    
    
    # SETUP SCENARIO
    Z2 = GF(2)
    x = word.polynomials(word.random(m*n), Z2, m)
    y = channel.erasure(x, t=t)
    
    if t > 0:
        F = GF(q)
        H = RS(F, (t,n))
    
        # PERFORM COMMUNICATION
        s = H * Matrix(x,F).T()
        s_disp = s.T().M[0]
    
        # BOB SOLVES FOR X USING Y AND S
        X = np.array([F.zero if i is None else i for i in y])   # pretend erasures are 0
        z = s - H * Matrix(X,F).T()                             # get right-hand side of equation
        locs = np.where([i==None for i in y])[0]                # find error locations
        h = H[:,locs]                                           # get left-hand side of equation
        e = solve(h, z)                                         # solve for our error
        X[locs] = e                                             # add in our error
    else:
        s_disp = ""
        X = y
    
    # DECIDE ON OUTPUT
    hex = int((m-1)/4)+1
    
    output = {"x":word.hexify(x, hex),
              "y":word.hexify(y, hex),
              "s":word.hexify(s_disp, hex),
              "X":word.hexify(X, hex)}
    
    return jsonify(output)


@app.route('/erasure/rn/optimize', methods=['POST'])
def erasure_rn_optimize():
    input = request.get_json()
    
    # PROCESS INPUT
    t = input['t']
    
    # FIND LEAST d
    d = -1
    Dp = excess(t,d+1)
    D = Dp + 1      # just whatever it must to get the loop to run
    while Dp < D:
        d += 1
        D = Dp
        Dp = excess(t,d+1)
    
    return jsonify({"d":d})

@app.route('/erasure/rn/simulate', methods=['POST'])
def erasure_rn_simulate():
    input = request.get_json()
    
    # PROCESS INPUT
    n = input['n']
    t = input['t']
    d = input['d']
    if 'seed' in input:
        np.random.seed(input['seed'])
        random.seed(input['seed'])
    
    # SETUP SCENARIO
    Z2 = GF(2)
    R = word.NUMPY(n, word.random(n))
    c = t + d
    
    x = word.random(n)
    y = channel.erasure(x, t=t)
    
    if t > 0:
        H = np.array([R.next() for i in range(c)])
        H = Matrix(H, Z2)
    
        # PERFORM COMMUNICATION
        s = H * Matrix(x,Z2).T()
        s_disp = s.T().M[0]
    
        # BOB SOLVES FOR X USING Y AND S
        X = np.array([0 if i < 0 else i for i in y])            # pretend erasures are 0
        S = s - H * Matrix(X,Z2).T()                            # get right-hand side of equation
        locs = np.where([i<0 for i in y])[0]                    # find error locations
        h = H[:,locs]                                           # get left-hand side of equation
        e = solve(h, S)                                         # solve for our error
        if e is None:
            X = y
        else:
            X[locs] = e                                         # add in our error
    else:
        s_disp = ""
        X = y
    
    # DECIDE ON OUTPUT
    output = {"x":word.strify(x),
              "y":word.strify(y),
              "s":word.strify(s_disp),
              "X":word.strify(X)}
    
    return jsonify(output)


if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0')    # public
    app.run(debug=True)                    # private
