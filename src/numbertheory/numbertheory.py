#!/usr/bin/env python

import math
from polynomial import Polynomial

''' gcf: a, b (both ints)
		returns the greatest common factor of a and b
		uses Euclid's recursive algorithm: O(log b)
		'''
def gcf(a,b):
	# ensure a is the smaller number
	if a > b:
		return gcf(b,a)
	r = b % a
	if r == 0:
		return a
	return gcf(r,a)

''' isprime: a (int)
		returns True iff a divides only a and 1
		uses brute-force algorithm: O(sqrt a)
		'''
def isprime(a):
	if a < 2:		# handle negatives and 1 immediately
		return False
	if a == 2:		# handle 2 separately since it's even and would mess up the next check
		return True
	if not a & 1:	# bitwise and: basically returns the last bit of a (0 iff even)
		return False
	if a < 9:		# everything else up to 9 is prime... this lets us start checking divisibility at 3
		return True
	
	max = int(math.sqrt(a))
	for i in range(3,max+1):	# try to divide everything up to sqrt a
		if a % i == 0:
			return False
	return True

''' nextprime: [a] (int)
		returns the smallest prime number greater than a
			if a is not given, uses a=1 (so it'll return 2)
		uses brute-force algorithm: Z(sqrt a)
		'''
def nextprime(a=1):
	if a < 2:		# handle negatives and 1 immediately
		return 2
	if a == 2:		# handle 3 separately since it's just one away from 2 and would mess up the process
		return 3
	while not isprime(a+2):
		a += 2
	return a+2

''' factor: a (int), [_f_] (dict int:int), [_p_] (int)
		returns prime factorization of a as a prime:power dictionary
		uses recursive algorithm: parameters _f_ and _p_ are only meant for recursion
		'''
def primefactor(a, _f_=None, _p_=None):
	if _f_ is None:		# if this is the first call in the recursion tree, initialize _f_ and _p_
		_f_ = {}
		_p_ = 2
	
	if isprime(a):		# base case: a is its own prime-factorization
		_f_[a] = _f_.get(a,0)+1
		return _f_
	(q, r) = divmod(a, _p_)
	if r == 0:
		_f_[_p_] = _f_.get(_p_,0)+1
		return primefactor(q, _f_=_f_, _p_=_p_)			# if _p_ worked, reuse it
	return primefactor(a, _f_=_f_, _p_=nextprime(_p_))	# otherwise, move to the next prime















# POLYNOMIAL VARIANTS

''' isirreducible: p (Polynomial)
		returns True iff p divides only p and 1
		uses brute-force algorithm: O(p)
		'''
def isirreducible(p):
	if not isinstance(p, Polynomial):
		raise TypeError("Argument must be a polynomial")
	
	if p[0] == p.F.zero:			# insofar as an x can be factored out, p is not irreducible
		return False					# (parity-check equivalent)
	if p.degree == 0:				# insofar as scalars are...scalar, p is irreducible . . . I guess
		return True						# I HONESTLY HAVE NO IDEA WHAT I'M DOING!!!
	
	# START AT X+1:
	#	dividing 1 is meaningless, and so in fact is dividing anything of degree 0
	q = Polynomial({0:p.F.one, 1:p.F.one}, p.F)
	while p.degree > q.degree:	# try to divide everything up to p's degree
		if p % q == p.F.zero:
			return False
		q = q.next()			# I feel like I ought to be skipping more than I am...
	return True
	# TODO: in point of fact, for this and the regular number variant, I need only...
	#		...divide by irreducibles/primes. There's some hard to analyse recursion...
	#		...but I think employing the nextirreducible/prime methods would be faster.

''' nextirreducible: p (Polynomial)
		returns the smallest irreducible polynomial number greater than p
		uses brute-force algorithm: Z(p)
		'''
def nextirreducible(p):
	p = p.next()
	while not isirreducible(p):
		p = p.next()
	return p

''' factor: p (Polynomial), [_f_] (dict Polynomial:int), [_p_] (Polynomial)
		returns prime factorization of p as a irreducible:power dictionary
		uses recursive algorithm: parameters _f_ and _p_ are only meant for recursion
		'''
def factor(p, _f_=None, _p_=None):
	if _f_ is None:		# if this is the first call in the recursion tree, initialize _f_ and _p_
		_f_ = {}
		_p_ = Polynomial({0:p.F.one, 1:p.F.one}, p.F)
	
	if isirreducible(p):		# base case: p is its own factorization
		_f_[p] = _f_.get(p,0)+1
		return _f_
	(q, r) = divmod(p, _p_)
	if r == p.F.zero:
		_f_[_p_] = _f_.get(_p_,0)+1
		return factor(q, _f_=_f_, _p_=_p_)			# if _p_ worked, reuse it
	return factor(p, _f_=_f_, _p_=nextirreducible(_p_))	# otherwise, move to the next prime

''' maps irreducible-polynomial degree m to k such that x**m + x**k + 1 '''
irreducibles = {
	2:1,3:1,4:1,5:2,6:1,7:1,9:1,
	10:3,11:2,12:3,14:5,15:1,17:3,18:3,
	20:3,21:2,22:1,23:5,25:3,28:1,29:2,
	30:1,31:3,33:10,34:7,35:6,36:9,39:4,
	41:3,42:7,44:5,46:1,47:5,49:9,
	52:3,
	60:1,
	71:6, 73:25,
	81:4,
	90:27,
	100:15,
	110:33,
	121:18,
	130:3,
	140:15,
	150:53,
	161:18,
	170:11,
	180:3,
	191:9,
	201:14,
	250:103,
	300:5,
	350:53,
	401:152,
	450:47,
	500:27,
	550:193,
	601:201,
	650:3,
	700:75,
	750:309,
	801:217,
	850:111,
	900:1,
	951:260,
	1001:17,
	1050:159,
	1100:35,
	1151:90,
	1201:171,
	1252:97,
	1300:75,
	1350:237,
	1401:92,
	1452:315,
	1478:69
	}

''' maps primitive polynomial degree m to a list of degrees k_i such that x**m + x**k_i + ... + 1 '''
primitives = {
	2:[1],3:[1],4:[1],5:[2],6:[1],7:[1],8:[6,5,1],9:[4],
	10:[3],11:[2],12:[7,4,3],13:[4,3,1],14:[12,11,1],15:[1],
	17:[3],19:[5,2,1],31:[3],61:[43,26,14],89:[38],107:[82,57,31],127:[1],
	229:[64,63,1],
	521:[32],607:[105],1279:[216],2203:[1656,1197,585],2281:[715],3217:[67],
	4253:[3297,2254,1093],4423:[271],9689:[84],9941:[7449,4964,2475],
	11213:[8218,6181,2304],19937:[881],21701:[15986,11393,5073],23209:[1530],44497:[8575]
}












