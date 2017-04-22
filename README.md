# information-reconciliation-Towson-thesis
Repository for Python code used in completing Master's thesis: Information Reconciliation for Erasure Channels

## Problem Statement
Say there are two binary strings of the same length, x and y, but t bits in y are "erased", meaning you can't tell if they're supposed to be 0's or 1's. What's the smallest number of bits the owner of x needs to send the owner of y in order for the latter to reconstruct x? The theoretical best we could do is in fact t bits, even though the owner of x has no idea which t bits are erased. But how do we do that? My thesis explores several protocols for achieving or nearly achieving optimum communication.

### Code Pieces
- Flask app to simulate nonbinary or probabilistic protocols with user-defined parameters
- Simulation ("multivariate.py") to record/analyse error-rate of probabilistic protocol
- Simulation ("reconciliation.py") to record/analyse runtime efficiency of nonbinary and probabilistic protocols

### Required Dependencies
(all of these are included with the Anaconda distribution of Python)
- numpy
- scipy
- flask
- pandas
- matplotlib

### How to run Flask app
1) set up workspace with the following files (/* indicates all files in directory)
  - src/communication/*
  - src/numbertheory/*
  - src/server.py
  - static/*
  - templates/*
2) run server.py (by default, requires localhost port 5000 to be free)
3) in any modern browser, go to http://localhost:5000/

### How to run simulations
1) set up workspace with the following files (/* indicates all files in directory)
  - src/communication/*
  - src/numbertheory/*
  - data/*
  - relevant files in src/simulations/, src/theory/, and src/analysis/ files
2) run desired file in src/simulations/ or src/analysis
