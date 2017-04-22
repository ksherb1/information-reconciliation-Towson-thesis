#!/usr/bin/env python

import numpy as np
from numbertheory.polynomial import Polynomial as P
import numbertheory.numbertheory as nt


''' random - returns a random string of length n, base q (default 2) '''
def random(n, q=2):
	return np.random.random_integers(0, q-1, size=n)



''' parity - returns whether the string has odd or even weight
		(only particularly meaningful for q=2)
		'''
def parity(x):
	cnt = 0
	for i in x:
		if i > 0:
			cnt += 1
	return cnt & 1


''' strify - a quick to-string method for strings '''
def strify(x):
	s = ""
	for i in range(len(x)):
		if (x[i] < 0):
			s += "X"
		else:
			s += str(x[i])
	return s

''' destrify - a quick array-from-binary string method '''
def destrify(x):
	return np.array([int(i) for  i in x], dtype=int)





"""
	there are three representations we care about
	1) bit array	- this is always an ndarray of ints
	2) array of "characters" - this is either an ndarray of ints or Polynomials
	3) string of characters - this is always a string
	"""

''' hexify - a quick string-from-array method for bits or polynomials
		m is # of characters per unit:
			increase to handle non-binary or very large polynomials '''
def hexify(x, m=1):
	s = ""
	for b in x:
		if m > 1:
			s += ' '
		if b is None or (not isinstance(b,P) and b < 0):	# erasure case
			s += '-'*m
		else:
			r = hex(int(b))[2:]		# first two characters of hex code are '0x'
			s += '0'*(m-len(r)) + r
	return s

''' polynomials: word (1d-array), F (FiniteField), m (int)
		returns an array of polynomials, grouping word into m-unit blocks
		F is the coefficient field these polynomials should have (usually Z2)
		'''
def polynomials(word, F, m):
	sections = range(0,len(word),m)
	return np.array([P(V,F) for V in np.split(word, sections[1:])])





# RANDOM BIT STREAMS: CONSTRUCTED WITH n AND seed, .next() gives n-bit word

''' NUMPY - a pseudo-random stream utilizing numpy.random '''
class NUMPY:
	''' NUMPY - n (int), seed (n-vector)
			PRE seed must be n-vector (compatibility purposes)
			'''
	def __init__(self, n, seed):
		if len(seed) != n:
			raise ValueError("Seed is incompatible length.")
		self.n = n
		seed_num = sum([(2**i)*seed[i] % 2147483647 for i in range(n)]) % 2147483647
		np.random.seed(seed_num)
	
	''' next - returns the next n-bit grouping of this generator '''
	def next(self):
		return np.random.random_integers(0,1, size=self.n)



''' LFSR - a pseudo-random Linear Feedback Shift Register generator '''
class LFSR:
	''' LFSR - n (int), seed (n-vector)
			PRE: seed must be n-vector
			'''
	def __init__(self, n, seed):
		if len(seed) != n:
			raise ValueError("Seed is incompatible length.")
		
		self.n = n
		
		if n in nt.primitives:
			self.pattern = np.zeros(n, dtype=int)
			self.pattern[0] = 1
			self.pattern[nt.primitives[n]] = 1
		else:
			raise ValueError("Must implement auto-primitive generation")
		
		self.current = seed
	
	''' next - returns the next n-bit grouping of this generator '''
	def next(self):
		bit = np.dot(self.pattern, self.current) & 1
		self.current = np.concatenate((self.current[1:], [bit]))
		return np.array(self.current)

''' RC4 - adaptation of RC4, a cryptographic stream-cipher pseudo-RNG '''
class RC4:
	''' RC4 - n (int), seed (list of ints)
			PRE: len(seed) cannot exceed 2**b
			'''
	def __init__(self, n, seed, b=8):
		if not len(seed) <= n:
			raise ValueError("Seed is incompatible length")
		
		self.n = n
		
		# Initialize state
		self.S = range(2**b)
		j = 0
		for i in range(2**b):
			j = (j + self.S[i] + seed[i%len(seed)]) % (2**b)
			self.S[i],self.S[j] = self.S[j],self.S[i]	# swap elements
		
		self.b = b
		self.i = 0
		self.j = 0
		self.buffer = ''
	
	''' next - returns the next n-bit grouping of this generator '''
	def next(self):
		# if the buffer is not long enough, add the next byte-like block
		while len(self.buffer) < self.n:
			self.i = (self.i + 1) % (2**self.b)
			self.j = (self.j + self.S[self.i]) % (2**self.b)
			
			self.S[self.i],self.S[self.j] = self.S[self.j],self.S[self.i]	# swap elements
			self.buffer += np.binary_repr(
								self.S[ (self.S[self.i]+self.S[self.j]) % (2**self.b)],
								width=self.b )
		
		ret = self.buffer[:self.n]
		self.buffer = self.buffer[self.n:]
		return destrify(ret)





