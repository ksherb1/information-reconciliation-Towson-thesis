#!/usr/bin/env python

import sys

import numpy as np
import random

from numbertheory.polynomial import Polynomial

'''
This module contains all the channel functions,
	which take a 1d-array of ints and spit out another,
	correlated but randomly changed, depending on the type of channel
'''

# the standard nothing-happened channel
def noiseless(x):
	y = np.copy(x)
	return y

'''
for each of these:	t = max number of bit issues
					p = probability of each bit having issue
note:	if additional parameters are not given
			they will act like a noiseless channel
		if both parameters are given
			method will throw an error
'''

# the standard flip-a-bit channel
def symmetric(x, t=0, p=0):
	if not t*p==0:
		sys.exit("Parameters t="+str(t)+" and p="+str(p)+" are incompatible.")
	
	y = np.copy(x)
	n = len(x)
	
	if not p==0:
		pattern = _p_pattern(n, p)
	else:
		pattern = _t_pattern(n, t)
	
	y[pattern] = (y[pattern]+1) % 2		# flip the bits
	return y

# bits may be erased (ie replaced with -1)
def erasure(x, t=0, p=0):
	if not t*p==0:
		sys.exit("Parameters t="+str(t)+" and p="+str(p)+" are incompatible.")
	
	y = np.copy(x)
	n = len(x)
	
	if not p==0:
		pattern = _p_pattern(n, p)
	else:
		pattern = _t_pattern(n, t)
	
	if isinstance(y[0], Polynomial):
		y[pattern] = None
	else:
		y[pattern] = -1		# "erase" the bits
	return y

# bits may be deleted (so the returned string is straight-up shorter)
def deletion(x, t=0, p=0):
	if not t*p==0:
		sys.exit("Parameters t="+str(t)+" and p="+str(p)+" are incompatible.")
	
	y = np.copy(x)
	n = len(x)
	
	if not p==0:
		pattern = _p_pattern(n, p)
	else:
		pattern = _t_pattern(n, t)
		
	y = np.delete(y, pattern)	# delete the bits
	return y

'''
helper methods
'''
def _t_pattern(n, t):
	return random.sample(range(n), t)

# samples each index from n at probability p
def _p_pattern(n, p):
	# check that p is valid probability:
	if not (0 <= p <= 1):
		sys.exit("Parameter p="+str(p)+" is not a valid probability [0,1].")
	
	# now maintain a pattern and add each index to it iff random number is within p
	pattern = []
	for i in range(n):
		if random.random() < p:
			pattern += [i]
	return pattern



