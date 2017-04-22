#!/usr/bin/env python

# SETUP

print "IMPORTING LIBRARIES...",
import pandas as pd
import matplotlib.pyplot as plt
print "DONE!"

# PLOTTER FUNCTIONS

''' Primary goal: plot time as a function of n, constrained to a particular t=f(n)
					do so for both RS and RN data
		'''

''' lookat - plot RS and RN data in dat as separate curves '''
def lookat(dat, plot, lab=None, color='k'):
	plot.plot(dat['N'], dat['RS_TIME']/dat['CNT'], color+'.', label="RS "+lab, markersize='10')	# RS plot
	plot.plot(dat['N'], dat['RN_TIME']/dat['CNT'], color+'s', label="RN "+lab)	# RN plot

''' xp - plot standard an**p curve '''
def xp(ns, p, a, plot, lab=None, pt='k-'):
	ns = sorted(ns)
	plot.plot(ns, [a*n**p for n in ns], pt, label=lab, linewidth='2')

# SCIENCE-Y FUNCTIONS

''' compare_dats - plot all RS and RN data in each data frame as separate curves'''
def compare_dats(dats, labs, colors):
	if(len(dats) is not len(labs) or len(labs) is not len(colors)):
		raise ValueError("Argument dimensions must match.")
	
	#fig = plt.figure().add_subplot(111, title="Average time to implement protocol",
	fig = plt.figure().add_subplot(111, title="",
								   xlabel="$n$", ylabel="Time (s)")
	fig.set_xscale('log', basex=2)
	fig.set_yscale('log', basey=2)
	
	for i in range(len(dats)):
		lookat(dats[i], fig, labs[i], colors[i])
	xp(dats[i]['N'], 3, 2**-19, fig, pt='k--', lab="$an^3$")
	xp(dats[i]['N'], 2, 2**-19, fig, pt='k-', lab="$an^2$")
	
	fig.legend(loc=0)

# DEFINE WHICH FILES TO LOOK AT

data_path = '../../data/reconciliation/'

print "READING FROM FILE...",
tenth = pd.read_csv(data_path+'tenth.dat')
quarter = pd.read_csv(data_path+'quarter.dat')
print "DONE!"



# ACTUAL SCRIPT
compare_dats(
		[tenth, quarter],
		['10%', '25%'],
		['b','g'])


plt.show()










