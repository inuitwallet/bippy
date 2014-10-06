import hashlib

import num.elip as elip
import num.enc as enc

def clockbase():
	"""
	256 bit hex: 4 x 16 byte long from float using clock (process time) + time (UTC epoch time)
	Note: not enough clock precision on Linuxes to be unique between two immediate calls
	"""
	from struct import pack
	from time import time, clock

	return pack('<dddd', clock(), time(), clock(), time()).encode('hex')

def clockrnd():
	"""
	512 bit int: random delay while hashing data,
	return result of 192-1725 time-based hashes.
	execution time on 2.8GHz Core2: 1.8-15.7ms
	"""
	loopcount = 64 + int(hashlib.sha256(clockbase()).hexdigest()[:3], 16)/8  # 64-575 loops, random
	hash1 = hash2 = int(clockbase()+clockbase(), 16)
	for i in xrange(loopcount):
		hash1 ^= int(hashlib.sha512(clockbase() + hashlib.sha512(clockbase()).hexdigest()).hexdigest(), 16)
		hash2 ^= int(hashlib.sha512((hex(hash1)) + ('%d' % hash1)).hexdigest(), 16)
	return hash1 ^ hash2
	
def entropy(entropy):
	"""
		512 bit random number from mouse co-ords and timer
	"""
	hashes = clockrnd()
	x = []
	y = []
	for coord in entropy:
		hashes ^= clockrnd()
		for char in str(coord[0]):
			x.append(char)
		for char in str(coord[1]):
			y.append(char)
	hashes ^= clockrnd()
	mouse = enc.sxor(x,y)
	return hashes ^ int(hashlib.sha512(str(mouse)*8).hexdigest(), 16)

def randomKey(entropy):
	"""
	256 bit number from equally strong urandom, user entropy, and timer parts
	"""
	if entropy.bit_length() < 250:
		print('Insufficient entropy parameter to generate key')
		return False
	from random import SystemRandom
	osrndi = SystemRandom()
	entstr = enc.encode(entropy, 16) + enc.encode(osrndi.getrandbits(512), 256) + str(clockrnd())
	osrnd = SystemRandom(entstr)
	privkey = 0
	while privkey < 1 or privkey > elip.N:
		privkey = enc.decode(hashlib.sha256(enc.encode(osrnd.getrandbits(512), 256)).digest(), 256) ^ osrnd.getrandbits(256)
		for lbit in xrange(clockrnd() % 64 + 64):
			clockstr = hex(clockrnd()) + str(clockrnd()) + entstr
			# Slice a moving 256 bit window out of SHA512
			clock32 = hashlib.sha512(clockstr).digest()[1+(lbit % 29): 33+(lbit % 29)]
			randhash = hashlib.sha512(enc.encode(osrnd.getrandbits(512), 256)).digest()[0+(lbit % 31): 32+(lbit % 31)]
			privkey ^= enc.decode(randhash, 256) ^ enc.decode(clock32, 256) ^ osrndi.getrandbits(256)
			osrnd = SystemRandom(hashlib.sha512(clock32 + randhash + entstr).digest())  # reseed
	return privkey
