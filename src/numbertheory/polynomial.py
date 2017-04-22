#!/usr/bin/env python

from functools import total_ordering
import numpy as np










''' Polynomial: implementation for polynomials, or more formally, vectors of field elements '''
@total_ordering				# I don't know what this means. We might have to import functools to get it to work
class Polynomial:
	''' Polynomial: V (see below), F (FiniteField)]
			if V is an int, this Polynomial evaluated at F.p equals V
			if V is a list, each element is the corresponding coefficient in the extension vector
			if V is a dictionary, each value is the coefficient of the corresponding key index
				in the latter two cases, each element of V must be in F
			'''
	def __init__(self, V, F):
		''' self._V_: dictionary representation of coefficient vector (power:coefficient) '''
		self._V_ = {}
		''' self.F: coefficient field '''
		self.F = F
		
		# FILL COEFFICIENT DICTIONARY
		if type(V) is int:
			# TODO: implement. Not sure how easy it is to do...
			
			pass
		elif type(V) is list or type(V) is np.ndarray:
			if any(v not in F for v in V):
				raise TypeError(str(V)+" contains elements which are not in "+str(self.F))
			for d in range(len(V)):
				self._V_[d] = V[d]
		elif type(V) is dict:
			if any(V[d] not in F for d in V):
				raise TypeError(str(V)+" contains elements which are not in "+str(self.F))
			for d in V:
				self._V_[d] = V[d]
		else:
			raise TypeError("V is not a valid type (must be int, list, or dict)")
		
		# CLEAR 0 VALUES FROM COEFFICIENT DICTIONARY
		for d in list(self._V_):
			if self._V_[d] == self.F.zero:
				del self._V_[d]
		
		# SET OTHER ATTRIBUTES
		self.degree = (max(self._V_) if len(self._V_) > 0 else -1)		# -1 so that len = degree +1 = 0
	
	
	
	
	
	# MAGIC CONTAINER METHODS
	
	''' len(Polynomial) is the max number of coefficients, or the degree plus one for the zero power '''
	def __len__(self):
		return self.degree + 1
	
	''' Polynomial[key] returns the coefficient for power key '''
	def __getitem__(self, key):
		if type(key) is not int:
			raise TypeError(str(key)+" is not a valid degree.")
		if key < 0:
			raise ValueError(str(key)+" is not a valid degree.")
		return self._V_.get(key, self.F.zero)
	
	
	
	
	
	
	
	# SPECIAL METHODS
	
	''' array: no parameters
			returns a list of coefficients, where the index refers to the degree
			'''
	def array(self):
		vector = np.zeros(len(self), dtype=(int if self.F.isintegerfield() else object))
		for d in self._V_:
			vector[d] = self[d]
		return vector
	
	''' solve: x (int or Polynomial)
			solves the polynomial at x
			key must be in F, as will be the result '''
	def solve(self, x):
		if x not in self.F:
			raise TypeError(str(x)+" is not an element of "+str(self.F))
		
		return sum( self[d] * x**d for d in self._V_ )
	
	''' write: [sym (string)]
			writes out the polynomial in classic V0 + V1 x + V2 x**2 + ... fashion
			optional sym(bol) replaces the 'x' character
			'''
	def write(self, sym='x'):
		# a rather elegant solution, but with crude output
		# ret = " + ".join( str(self.V.get(d,0))+" "+sym+"**"+d for d in range(len(self))[::-1] )
		
		ds = list(self._V_)
		ds.sort()
		
		if len(ds) == 0:		# if polynomial has no coefficients, it's simply 0
			return "0"
		
		ret = ""
		
		# first two degrees are special
		if ds[0] == 0:
			ret += str(self[0])+" + "
			ds = ds[1:]
		if len(ds) > 0 and ds[0] == 1:
			if self[1] != 1:
				ret += str(self[1])+" "
			ret += sym+" + "
			ds = ds[1:]
		for d in ds:
			if self[d] != 1:
				ret += str(self[d])+" "
			ret += sym+"**"+str(d)+" + "
		return ret[:-3]			# cut out the last " + "
	
	''' next: returns the next highest polynomial with coefficients in F '''
	def next(self):
		V = self._V_.copy()
		
		d = 0
		while True:		# stop condition is when we get incrementing a coefficient gives a non-zero
			if self.F.isintegerfield():
				V[d] = self.F[ V.get(d, 0) + 1 ]
			else:
				V[d] = V.get(d, self.F.zero).next()
		
			if not V[d] == self.F.zero:
				return Polynomial(V, self.F)
			d += 1
		# we're guaranteed to return something eventually
	
	
	
	# MISCELLANEOUS MAGIC METHODS
	
	''' str(Polynomial) returns a string of coefficients, leading with the degree coefficient
			if F requires all coefficients are single digits, there is no delimiter
			if F allows larger digits (but still digits), coefficients are separated by space
			if elements of F are polynomials, each is in brackets and separated by space
			'''
	def __str__(self):
		if len(self) == 0:
			return "0"
		if not self.F.isintegerfield():		# coefficients are polynomials
			return " ".join( "["+str(self[d])+"]" for d in range(len(self))[::-1] )
		if self.F.p > 10:
			return " ".join( str(self[d]) for d in range(len(self))[::-1] )
		return "".join( str(self[d]) for d in range(len(self))[::-1] )
	
	''' repr(Polynomial) does the same as str '''
	def __repr__(self):
		return str(self)
	
	
	''' int(Polynomial) gives the "order" i, where this polynomial is the i-th largest polynomial in F above 0
			this is, very conveniently, simply solving the polynomial at F.P
			'''
	def __int__(self):
		return int(self.solve(self.F.P))			# if field is GF(p^m), solve(F.P) is a polynomial and we need recursion
	
	''' hash(Polynomial) is the same as int '''
	def __hash__(self):
		return int(self)
	
	
	''' p1 == p2 iff p1 and p2 have identical coefficients
			for convenience, comparisons to 0 and 1 are allowed
			all other incompatible arguments, including polynomials with different coefficient fields, return false
			'''
	def __eq__(self, other):
		if not isinstance(other, Polynomial):
			if other == 0:
				return len(self) == 0
			if other == 1:
				return len(self) == 1 and self[0] == 1
			return False
		if not self.F == other.F:
			return False
		return self._V_ == other._V_
	
	''' p1 > p2 iff int(p1) > int(p2)
			if the coefficient fields don't match, these polynomials are incomparable and a ValueError is raised
			'''
	def __gt__(self, other):
		if not isinstance(other, Polynomial):
			raise TypeError("Cannot compare polynomial to "+str(other))
		if not self.F == other.F:
			raise ValueError("Polynomial arguments have different coefficient fields. Cannot compare.")
		return int(self) > int(other)
	
	# TODO: other comparisons may be required
	
	
	
	
	
	# POLYNOMIAL ARITHMETIC
	
	#	-- UNARY OPERATORS --
	
	''' -p1 has additive inverse of each coefficient of p1 '''
	def __neg__(self):
		V = {}
		for d in self._V_:
			V[d] = self.F.neg( self[d] )
		return Polynomial(V, self.F)
	
	#	-- NORMAL OPERATORS --
	
	''' p1 + p2 is element-wise addition of each element
			for convenience, addition by zero is also supported
			'''
	def __add__(self, other):
		if not isinstance(other, Polynomial):
			if other == 0:
				return self
			raise TypeError("Cannot add "+str(other)+" to a Polynomial")
		if not self.F == other.F:
			raise ValueError("Polynomial arguments have different coefficient fields. Cannot add.")
		
		V = {}
		for d in list(set(self._V_)|set(other._V_)):
			V[d] = self.F[ self[d]+other[d] ]
		return Polynomial(V, self.F)
	
	''' p1 - p2 is, naturally, p1 + -p2 '''
	def __sub__(self, other):
		if not isinstance(other, Polynomial):
			raise TypeError("Cannot subtract "+str(other)+" from a Polynomial")
		
		return self + (-other)
	
	''' p1 * p2 is distributed multiplication of all elements, with like degrees added
			for convenience, multiplication by 0 and 1 is also supported
			'''
	def __mul__(self, other):
		if not isinstance(other, Polynomial):
			if other == 0:
				return Polynomial({0:self.F.zero}, self.F)
			if other == 1:
				return self
			raise TypeError("Cannot multiply "+str(other)+" with a Polynomial")
		if not self.F == other.F:
			raise ValueError("Polynomial arguments have different coefficient fields. Cannot multiply.")
		
		V = {}
		for d1 in self._V_:
			for d2 in other._V_:
				V[d1+d2] = self.F[ V.get(d1+d2, self.F.zero) + self[d1]*other[d2] ]
		
		return Polynomial(V, self.F)
	
	''' p1 ** n is repeated multiplication of p1 with itself '''
	def __pow__(self, other):
		if type(other) is not int:
			raise TypeError("Polynomials can only be raised to integer powers.")
		if other < 0:
			raise ValueError("Negative exponents of polynomials are not supported. Use FiniteField.inv() instead.")
		
		p = self.F.one
		for i in range(other):
			p = p * self
		return p
	
	''' divmod(p1, p2) does long division of p1 and p2
			for convenience, division by 1 is also supported
			'''
	def __divmod__(self, other):
		if not isinstance(other, Polynomial):
			if other == 1:
				return self
			raise TypeError(str(other)+" cannot divide a Polynomial")
		if not self.F == other.F:
			raise ValueError("Polynomial arguments have different coefficient fields. Cannot divide.")
		
		q = {}								# coefficients for the quotient
		r = Polynomial(self._V_, self.F)	# polynomial for remainder
		
		while r.degree >= other.degree:			# TODO: this may be tricksier in F.p > 2
			# c * x**d   is the leading term of the quotient not yet calculated
			c = self.F[ r[r.degree] * self.F.inv(other[other.degree]) ]
			d = r.degree - other.degree
			
			q[d] = c							# add this term to the quotient
			
			p = {}
			for i in other._V_:					# craft the total contribution from q[d]
				p[i+d] = other[i]
			
			r = r - Polynomial(p, self.F)		# update remainder after this iteration
		
		return (Polynomial(q, self.F), r)
	
	''' p1 // p2 is the quotient portion of divmod(p1,p2) '''
	def __floordiv__(self, other):
		(q,r) = divmod(self, other)
		return q
	
	''' p1 % p2 is the remainder portion of divmod(p1,p2) '''
	def __mod__(self, other):
		(q,r) = divmod(self, other)
		return r


