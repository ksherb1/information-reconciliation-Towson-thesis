#!/usr/bin/env python

import numbertheory as nt
from polynomial import Polynomial

''' FiniteField: immutable finite field for performing algebraic operations '''
class FiniteField:
	''' FiniteField: p, [m] (both ints)
			if m is omitted, p is the number of elements in the field
				in this case, p should be a power of a prime
			if m is given, p is the (prime) characteristic and m is its power
			'''
	def __init__(self, p, m=None):
		if m is None:		# if m is none, p must be a power of a prime
			# the factorization of p returns a dictionary (prime:power)
			factors = nt.primefactor(p)
			if len(factors) > 1:
				raise ValueError("Could not generate GF("+str(p)+"): "+str(p)+" is not the power of a prime")
			
			# now task p and m to characteristic and power, respectively
			p = list(factors)[0]	# note p is unchanged if m is 1
			m = factors[p]
		
		''' self.p: the characteristic of the field
					IE the smallest n for which n*x=0 for ALL x in field '''		
		self.p = p
		''' self.order: the number of elements in the field '''
		self.order = p**m
		
		
		# the following attributes are subtly different depending on whether the order is prime
		''' self.GF_p: the field GF(p) '''
		''' self.P: the modulus of the field '''
		''' self.zero: additive identity '''
		''' self.one: zero identity '''
		''' self.alpha: an (arbitrary) primitive element '''
		if m == 1:
			self.GF_p = self
			self.P = p			# GF(p) is simply Z_p
			self.zero = 0
			self.one = 1
		else:
			self.GF_p = FiniteField(p)
			# GF(p^m) is Z_p[x]/P(x), where P is an irreducible polynomial of degree m in Z_p[x]
			self.P = nt.nextirreducible(Polynomial({0:1, m:1}, self.GF_p))
			self.zero = Polynomial({0:0}, self.GF_p)
			self.one = Polynomial({0:1}, self.GF_p)
		
		''' self._neg_: holds additive inverses. built as needed '''
		self._neg_ = {}
		''' self._inv_: holds multiplicative inverses. built as needed '''
		self._inv_ = {}
	
	''' isintegerfield: returns True iff elements of this field are ints (as opposed to Polynomials) '''
	def isintegerfield(self):
		return self.order == self.p
	
	
	# MISCELLANEOUS METHODS
	
	''' alpha: returns the first primitive element of this field '''
	def alpha(self):
		for a in self:	# this goes through zero, too, but meh...
			apow = self.one		# a^i starts at a^0 == 1
			for i in range(1, self.order-1):
				apow = self[a*apow]
				if apow == self.one:
					break
			else:		# this goes if 1 hasn't been seen yet OR if loop never ran (ie GF(2))
				apow = self[a*apow]		# a^(order-1) SHOULD be 1
				if apow == self.one:
					return a
	
	
	
	# INVERSION METHODS
	
	''' neg: x (int or Polynomial)
			returns the additive inverse of element x
			uses a very naive iterative search, but stores results dynamically
			'''
	def neg(self, x):
		if x not in self:
			raise TypeError(str(x)+" is not an element of "+str(self))
		if x in self._neg_:
			return self._neg_[x]
		for e in self:
			if e in self._neg_:
				if self._neg_[e] == x:
					self._neg_[x] = e
					return e
			else:
				y = self[ x + e ]
				if y == self.zero:
					self._neg_[x] = e
					return e
		# we're guaranteed to have returned something, since we're in a field
	
	
	''' inv: x (int or Polynomial)
			returns the multiplicative inverse of element x
			uses a very naive iterative search, but stores results dynamically
			'''
	def inv(self, x):
		if x not in self:
			raise TypeError(str(x)+" is not an element of "+str(self))
		if x == self.zero:
			raise ZeroDivisionError("0 does not have an inverse. Ever.")
		if x in self._inv_:
			return self._inv_[x]
		for e in self:
			if e in self._inv_:
				if self._inv_[e] == x:
					self._inv_[x] = e
					return e
			else:
				y = self[ x * e ]
				if y == self.one:
					self._inv_[x] = e
					return e
		# we're guaranteed to have returned something, since we're in a field
	
	
	''' GF1 == GF2 iff they have the same order. That's proven somewhere... '''
	def __eq__(self, other):
		if not isinstance(other, FiniteField):
			raise TypeError("Cannot compare finite field to "+str(other))
		return self.order == other.order
	
	# MAGIC CONTAINER METHODS
	
	''' len(FiniteField) is the same as the order '''
	def __len__(self):
		return self.order
	
	''' FiniteField[key] returns the element e in _elems_ which has e == key mod P '''
	def __getitem__(self, key):
		if key not in self:
			raise TypeError(str(key)+" is not an element of "+str(self))
		
		return key % self.P		# if field is GF(p^m), key % P is a polynomial
	
	''' v in FiniteField if v is equivalent to some element of the field:
			order is characteristic (so GF(n)=Z_p), and v is int... OR
			m > 1 and v is Polynomial with coefficient field = GF(p)
			'''
	def __contains__(self, v):
		if self.isintegerfield():
			return isinstance(v, int)
		if self.order > self.p:
			return isinstance(v, Polynomial) and v.F.order == self.p
		return False
	
	''' iterator starts at zero and goes through all order elements '''
	def __iter__(self):
		return FiniteFieldIterator(self)
	
	
	
	
	# MISCELLANEOUS MAGIC METHODS
	
	''' str(FiniteField) gives GF(order) '''
	def __str__(self):
		return "GF("+str(self.order)+")"
	
	
	
	
	
	











''' FiniteFieldIterator: iterator object to traverse an entire FiniteField '''
class FiniteFieldIterator:
	''' FiniteFieldIterator: F (FiniteField)
			F is the FiniteField to be iterated over,
				starting at F.zero and going through all F.order elements
			'''
	def __init__(self, F):
		''' self.F: the FiniteField we are iterating over '''
		self.F = F
		''' self.n: the next element to be returned '''
		self.n = F.zero
		''' self.i: the number of elements we have thus-far returned '''
		self.i = 0
	
	''' as per protocol, __iter__ returns self '''
	def __iter__(self):
		return self
	
	''' next: finds the next largest polynomial and returns it '''
	### TODO: python3 compatibility changes the name of this method to __next__(self)
	def next(self):
		if self.i == self.F.order:
			raise StopIteration()
		
		next = self.n					# save this to return after updates
		
		if self.F.isintegerfield():		# GF(p) contains simple integers
			self.n += 1
		else:							# GF(p^m) contains polynomials in Z_p[x]
			self.n = self.n.next()
		self.i += 1
		
		return next
	













