import encrypt.scrypt as scrypt
import encrypt.aes as aes
import num.enc as enc
import hashlib
import math

import res.wordlists.electrum as wlist
words = wlist.words

n = 1626

def encrypt(seed, passphrase):
	"""
		Encrypt the Electrum seed
	"""
	#1. Decode the seed value to the original number
	seed = mn_decode(seed.split())

	#2. Take a hash of the decoded seed to act as a scrypt salt
	salt = hashlib.sha256(hashlib.sha256(seed).digest()).digest()[:4]

	#3. Derive a key from the passphrase using scrypt
	key = scrypt.hash(passphrase, salt, 16384, 8, 8)

	#4. Split the key into half 1 and half 2
	derivedhalf1 = key[0:32]
	derivedhalf2 = key[32:64]

	#5. Do AES256Encrypt(seedhalf1 xor derivedhalf1[0...15], derivedhalf2), call the 16-byte result encryptedhalf1
	# (Electrum may change the number of words in a seed so we should future proof by just using the halves rather than hardcoded lengths)
	Aes = aes.Aes(derivedhalf2)
	encryptedhalf1 = Aes.enc(enc.sxor(seed[:int(math.floor(len(seed) / 2))], derivedhalf1[:16]))

	#6. Do AES256Encrypt(seedhalf2 xor derivedhalf1[16...31], derivedhalf2), call the 16-byte result encryptedhalf2
	encryptedhalf2 = Aes.enc(enc.sxor(seed[int(math.floor(len(seed) / 2)):len(seed)], derivedhalf1[16:32]))

	#7. The encrypted private key is the Base58Check-encoded concatenation of the following
	# \x4E\xE3\x13\35 + salt + encryptedhalf1 + encryptedhalf2
	encSeed = '\x4E\xE3\x13\x35' + salt + encryptedhalf1 + encryptedhalf2
	check = hashlib.sha256(hashlib.sha256(encSeed).digest()).digest()[:4]
	return enc.b58encode(encSeed + check)

def decrypt(encSeed, passphrase):
	"""
		Decrypt an Electrum seed encrypted with the above method
	"""
	#1. Base 58 decrypt the encrypted key
	# get the two encrypted halves, the check and the salt
	decSeed = enc.b58decode(encSeed)
	check = decSeed[-4:]
	#check that it's not been tampered with
	if check != hashlib.sha256(hashlib.sha256(decSeed[:-4]).digest()).digest()[:4]:
		return False, 'checksum'

	salt = decSeed[4:8]
	encryptedhalfs = decSeed[8:len(decSeed)-4]
	encryptedhalf1 = encryptedhalfs[0:int(math.floor(len(encryptedhalfs) / 2))]
	encryptedhalf2 = encryptedhalfs[int(math.floor(len(encryptedhalfs) / 2)):]

	#2. Derive the decryption key using scrypt
	key = scrypt.hash(passphrase, salt, 16384, 8, 8)
	derivedhalf1 = key[0:32]
	derivedhalf2 = key[32:64]

	#3. Decrypt the encrypted halves
	Aes = aes.Aes(derivedhalf2)
	decryptedhalf1 = Aes.dec(encryptedhalf1)
	decryptedhalf2 = Aes.dec(encryptedhalf2)

	#4 . xor them with the two halves of derivedhalf1 to get the original values
	half1 = enc.sxor(decryptedhalf1, derivedhalf1[:16])
	half2 = enc.sxor(decryptedhalf2, derivedhalf1[16:32])

	#5. build the seed and check it against the check hash
	seed = half1 + half2
	if salt != hashlib.sha256(hashlib.sha256(seed).digest()).digest()[:4]:
		return False, 'salt'

	#6. encode the seed as an Electrum Mnemonic list
	mn = mn_encode(str(seed))

	#6 . return the mnemonic as a single string
	seed = ''
	for word in mn:
		seed += word + ' '
	return True, seed

def buildRandom():
	"""
		Generate a random assortment of electrum Worrds.
		WARNING - DO NOT USE THIS FUNCTION TO GENERATE AN ELECTRUM SEED
	"""
	import random
	outWords = ''
	for i in xrange(0,12):
		word = words[random.randint(0,(len(words)-1))]
		outWords += word + ' '
	return outWords

def mn_encode( message ):
	assert len(message) % 8 == 0
	out = []
	for i in range(len(message)/8):
		word = message[8*i:8*i+8]
		x = int(word, 16)
		w1 = (x%n)
		w2 = ((x/n) + w1)%n
		w3 = ((x/n/n) + w2)%n
		out += [ words[w1], words[w2], words[w3] ]
	return out

def mn_decode( wlist ):
	out = ''
	for i in range(len(wlist)/3):
		word1, word2, word3 = wlist[3*i:3*i+3]
		w1 =  words.index(word1)
		w2 = (words.index(word2))%n
		w3 = (words.index(word3))%n
		x = w1 +n*((w2-w1)%n) +n*n*((w3-w2)%n)
		out += '%08x'%x
	return out
