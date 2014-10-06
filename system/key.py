import re
import json
import hashlib
import num.enc as enc
import encrypt.electrum as electrum
import encrypt.bip39 as bip39

def isWif(key, currency):
	if re.search("^[a-km-zA-HJ-NP-Z0-9]{52}", key):
		if checkChecksum(key):
			return True, 'compressed'
		else:
			return True, 'badchecksum'
	if re.search("^[a-km-zA-HJ-NP-Z0-9]{51}", key):
		if checkChecksum(key):
			return True, 'uncompressed'
		else:
			return True, 'badchecksum'
	else:
		return False, 'notwif'

def isBip(key, currency):
	with open('res/json/currencies.json', 'r') as dataFile:
		currencies = json.load(dataFile)	
	for cur in currencies:
		if cur['currency'] == currency:
			break
	if re.search('^' + cur['bipPrefix'] + '[a-km-zA-HJ-NP-Z0-9]{56}$', key):
		if checkChecksum(key):
			return True, 'good'
		else:
			return True, 'badchecksum'
	else:
		return False, 'bad'
		
def isHex(key):
	if re.search('[0-9A-F]{64}$', key):
		return True
	else:
		return False
		
def isBase64(key):
	if re.search('^[A-Za-z0-9=+\/]{44}$', key):
		return True
	else:
		return False
		
def isBase6(key):
	if re.search('^[1-6]{99}$', key):
		return True
	else:
		return False

def isElectrumSeed(key):
	key = key.split()
	if len(key) == 12:
		for word in key:
			if word not in electrum.words:
				return True, 'invalid word'
		return True, 'seed'
	else:
		return False, 'wrong length'

def isEncElectrumSeed(key):
	if re.search('^SeedE[a-km-zA-HJ-NP-Z0-9]{55}$', key):
		if checkChecksum(key) is False:
			return True, 'checksum'
		else:
			return True, 'valid'
	else:
		return False, 'not valid'

def isBip39Seed(key):
	key = key.split()
	if len(key) == 12:
		for word in key:
			if word not in bip39.words:
				return False, 'invalid word'
		return True, 'seed'
	else:
		return False, 'wrong length'

def isAddress(key, currency):
	"""
		check that the supplied value is a valid address for the chosen currency
	"""
	if re.search("^[a-km-zA-HJ-NP-Z0-9]{26,35}$", key):
		if checkChecksum(key) is False:
			return True, 'checksum'
		with open('res/json/currencies.json', 'r') as dataFile:
			currencies = json.load(dataFile)
		for cur in currencies:
			if cur['currency'] == currency:
				break
		prefixes = cur['prefix'].split('|')
		if key[0] not in prefixes:
			return True, 'prefix'
		return True, 'address'
	else:
		return False, 'not valid'

def isEncAddress(key):
	"""
		check if the supplied text is a valid encrypted public address
	"""
	if re.search('^EAddr38[a-km-zA-HJ-NP-Z0-9]{56}$', key):
		if checkChecksum(key) is False:
			return True, 'checksum'
		return True, 'good'
	else:
		return False, 'not valid'


def privKeyVersion(privK, cur, isCompressed = True):
	"""
		determine what sort of private key we have
		convert it to raw (base 10) and return

		No need to alert to a bad checksum as this should have already been checked in the input check
	"""
	isWIF, comment = isWif(privK, cur)
	if isWIF is True:
		if isCompressed is True:
			privK = enc.decode(enc.encode(enc.decode(privK, 58), 256)[1:-5], 256)
		else:
			privK = enc.decode(enc.encode(enc.decode(privK, 58), 256)[1:-4], 256)
	elif isHex(privK):
		privK = enc.decode(privK, 16)
	elif isBase64(privK):
		privK = privK.decode('base64', 'strict')
	elif isBase6(privK):
		privK = privK.decode('base6', 'strict')
	return privK

def checkChecksum(key):
	"""
		requires a base58_Check encoded string.
		calculates the hash of the key and compare to the checksum
	"""
	#decode to base256
	checkKey = enc.b58decode(key)
	checksum = checkKey[-4:]
	hash = hashlib.sha256(hashlib.sha256(checkKey[:-4]).digest()).digest()[:4]
	if hash == checksum:
		return True
	else:
		return False
