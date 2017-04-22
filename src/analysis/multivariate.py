#!/usr/bin/env python

# SETUP

print "IMPORTING LIBRARIES...",
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from theory.multivariate import E, D, d_min
from theory.multivariate import ratioofn, logofn
print "DONE!"

# PLOTTER FUNCTIONS

''' Primary goal: compare probabilistic data to theoretical results
		'''

''' simple plotters for an individual data frame, with various constraints '''
def errorrate(dat, n, plot, lab=None, pt='.'):
	mask = (dat['N']==n) & (dat['T']==dat['C'])
	plot.plot(dat['T'][mask], dat['EPS'][mask], pt, label=lab)
def extrabits(dat, n, t, plot, lab=None, pt='.'):
	mask = (dat['N']==n) & (dat['T']==t)
	plot.plot(dat['C'][mask]-t, dat['EPS'][mask], pt, label=lab)
def extrabits_excess(dat, n, t, plot, lab=None, pt='.'):
	mask = (dat['N']==n) & (dat['T']==t)
	excess = dat['C'][mask]/(1-dat['EPS'][mask]) - t
	plot.plot(dat['C'][mask]-t, excess, pt, label=lab)
def min_excess(dat, n, plot, lab=None, pt='.'):
	records = dat[['T','C','EPS']][dat['N']==n]
	records['D'] = records['C']/(1-records['EPS']) - records['T']
	info = records.groupby(['T'], as_index=False)['D'].min()	# info holds 'T' -> min 'D'
	plot.plot(info['T'], info['D'], pt, label=lab)
def min_excess_over_n(dat, t_fun, plot, lab=None, pt='.'):
	records = dat[['N','T','C','EPS']][dat['T']==t_fun(dat['N'])]
	records['D'] = records['C']/(1-records['EPS']) - records['T']
	info = records.groupby(['N'], as_index=False)['D'].min()	# info holds 'T' -> min 'D'
	plot.plot(info['N'], info['D'], pt, label=lab)

''' THEORETICAL PLOTTERS '''
def errorrate_theory(n, plot, lab='Perfect Randomness', pt='k-'):
	ts = range(1,n+1)
	epss = [E(t,0) for t in ts]
	plot.plot(ts, epss, pt, label=lab)
def extrabits_theory(t, dC, plot, lab='Perfect Randomness', pt='k-'):
	ds = range(dC)
	epss = [E(t,d) for d in ds]
	plot.plot(ds, epss, pt, label=lab)
def extrabits_excess_theory(t, dC, plot, lab='Perfect Randomness', pt='k-'):
	ds = range(1,dC)
	Ds = [D(t,d) for d in ds]
	plot.plot(ds, Ds, pt, label=lab)
def min_excess_theory(n, plot, lab='Perfect Randomness', pt='k-'):
	ts = range(1,n+1)
	Ds = [D(t,d_min(t)) for t in ts]
	plot.plot(ts, Ds, pt, label=lab)
	plot.plot(ts, 1+np.log2(ts), 'm-', label="My Guess")
def min_excess_over_n_theory(max_n, t_fun, plot, lab=None, pt='.'):
	ns = np.arange(1,max_n+1,dtype=int)
	ts = t_fun(ns)
	Ds = [D(int(t),d_min(t)) for t in ts]	# the weird 'int' cast is so Python bothers overflow management
	plot.plot(ns, Ds, pt, label=lab)

# SCIENCE-Y FUNCTIONS

''' compare_dats - dats (list of DataFrames)
		compare error-rate between various data sets (ex. between different RNG techniques)
		will create and return a new figure
		'''
def compare_dats(dats, labs, pts, n, theory=False):
	fig = plt.figure().add_subplot(111, title="Error-rate at n="+str(n)+", using exactly t words",
								   xlabel="t", ylabel="eps", ylim=(0,1))
	if theory:
		errorrate_theory(n, fig)
	
	for i in range(len(dats)):
		errorrate(dats[i], n=n, plot=fig, lab=labs[i], pt=pts[i])
	
	return fig


''' compare_n - dat(DataFrame), ns (list of ints)
		show how error rate changes with n
		will create and return a new figure
		'''
def compare_n(dat, ns, labs, pts, theory=False):
	fig = plt.figure().add_subplot(111, title="Error-rate using exactly t words",
								   xlabel="t", ylabel="$\epsilon$", ylim=(0,1))
	if theory:
		errorrate_theory(max(ns), fig)
	
	for i in range(len(ns)):
		errorrate(dat, n=ns[i], plot=fig, lab=labs[i], pt=pts[i])
	
	return fig

''' compare_ts_extrabits - dat(DataFrame), ts (list of ints)
		show how error rate changes as c is increased one by one
		will create and return a new figure
		'''
def compare_ts_extrabits(dat, ts, labs, pts, n, theory=False):
	fig = plt.figure().add_subplot(111, title="Error-rate as words are added incrementally",
								   xlabel="c-t", ylabel="$\epsilon$", ylim=(0,1))
	if theory:
		extrabits_theory(max(ts), 16, fig)
	
	for i in range(len(ts)):
		extrabits(dat, n=n, t=ts[i], plot=fig, lab=labs[i], pt=pts[i])
	
	return fig

''' compare_ts_extrabits_excess - dat(DataFrame), ts (list of ints)
		show how excess complexity changes as c is increased one by one
		will create and return a new figure
		'''
def compare_ts_extrabits_excess(dat, ts, labs, pts, n, theory=False):
	fig = plt.figure().add_subplot(111, title="Excess Communication Complexity",
								   xlabel="c-t", ylabel="$\Delta_c$")
	if theory:
		extrabits_excess_theory(max(ts), 16, fig)
	
	for i in range(len(ts)):
		extrabits_excess(dat, n=n, t=ts[i], plot=fig, lab=labs[i], pt=pts[i])
	
	return fig

''' compare_n_min_excess - dat(DataFrame), ns (list of ints)
		show how lowest achievable excess communication changes with n
		will create and return a new figure
		'''
def compare_n_min_excess(dat, ns, labs, pts, theory=False):
	fig = plt.figure().add_subplot(111, title="Best Achievable Communication Complexity",
								   xlabel="t", ylabel="$\Delta_c$")
	if theory:
		min_excess_theory(max(ns), fig)
	for i in range(len(ns)):
		min_excess(dat, n=ns[i], plot=fig, lab=labs[i], pt=pts[i])


''' compare_min_excess_over_n - dat(DataFrame), t_funs (int array->int array function)
		fixing t by each t_fun(n), plot lowest achievable excess communication over n
		will create and return a new figure
		'''
def compare_min_excess_over_n(dat, t_funs, labs, pts, theory=False):
	fig = plt.figure().add_subplot(111, title="Best Achievable Communication Complexity - t fixed",
								xlabel="n", ylabel="$\Delta_c$")
	for i in range(len(t_funs)):
		min_excess_over_n(dat, t_fun=t_funs[i], plot=fig, lab=labs[i], pt=pts[i])
		
	if theory:
		for t_fun in t_funs:
			min_excess_over_n_theory(max(dat['N']), t_fun=t_fun, plot=fig, pt='-')
	


# DEFINE WHICH FILES TO LOOK AT

data_path = '../../data/multivariate/'

print "READING FROM FILE...",
NUMPY = pd.read_csv(data_path+'NUMPY.dat')
LFSR = pd.read_csv(data_path+'LFSR.dat')

print "DONE!"



# ACTUAL SCRIPT




# EXAMINE NUMPY DATA MORE CLOSELY

compare_n(NUMPY,
		[5, 15, 127],
		['5','15','127'],
		['.', 'x', '+'],
		theory=True)
compare_ts_extrabits(NUMPY,
		[10,55,127],
		['10','55','100'],
		['.', 'x', '+'],
		n = 127,
		theory=False)
compare_ts_extrabits_excess(NUMPY,
		[10,55,127],
		['10','55','100'],
		['.', 'x', '+'],
		n = 127,
		theory=False)

compare_n_min_excess(NUMPY,
		[5, 15, 127],
		['5','15','127'],
		['.', 'x', '+'],
		theory=True)


compare_min_excess_over_n(NUMPY,
		[ratioofn(.1), ratioofn(.25), logofn(2)],
		['$t=\lceil n/10\lceil$','$t=\lceil n/4\lceil$','$t=\lceil\log_2{n}\lceil$'],
		['.', 'x', '+'],
		theory=True)

# COMPARE NUMPY AND LFSR

compare_dats([NUMPY, LFSR],
			 ['NUMPY', 'LFSR'],
			 ['.', 'x'],
			 n = 15,
			 theory=True)

compare_dats([NUMPY, LFSR],
			 ['NUMPY', 'LFSR'],
			 ['.', 'x'],
			 n = 127,
			 theory=True)



plt.show()




