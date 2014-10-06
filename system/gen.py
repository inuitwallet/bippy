import json
import random
import hashlib

import encrypt.bip38 as bip38
import num.enc as enc
import system.key as key
import num.rand as rand
import system.address as address

def genBIPKey(currency, passphrase, entropy='', privateKey='', isCompressed=True):
	"""
	Generate a BIP38 privatekey + public address#
	"""
	#using the currencies.json file, get the currency data
	with open('res/json/currencies.json', 'r') as dataFile:
		currencies = json.load(dataFile)
	for cur in currencies:
		if cur['currency'] == currency:
			break
	#randomly choose a prefix if multiples exist
	prefixes = cur['prefix'].split('|') 
	prefix = prefixes[random.randint(0, (len(prefixes) - 1))]
	#generate the private and public keys
	if privateKey == '':
		privateKey = int(rand.randomKey(rand.entropy(entropy)))
	privK256 = enc.encode(privateKey, 256, 32)
	publicAddress = address.publicKey2Address(address.privateKey2PublicKey(privateKey, isCompressed), int(cur['version']), prefix, int(cur['length']))
	#BIP38 encryption
	BIP = bip38.encrypt(privK256, publicAddress, str(passphrase), 8)
	return BIP, publicAddress
	
def encBIPKey(privK, cur, passphrase, isCompressed=True):
	"""
	Encrypt an existing private key with BIP38
	"""
	#we need to check what type of private key we are working with and change it to raw (base10)
	privK = key.privKeyVersion(privK, cur, isCompressed)
	#once we have this we can use the function above to generate the BIP keys
	BIP, publicAddress = genBIPKey(cur, passphrase, '', privK, isCompressed)
	return BIP, publicAddress

def decBIPKey(encrypted_privK, passphrase, currency):
	"""
	Decrypt an encrypted Private key
	Show the corresponding public address
	"""
	#using the currencies.json file, get the currency data
	with open('res/json/currencies.json', 'r') as dataFile:
		currencies = json.load(dataFile)
	for cur in currencies:
		if cur['currency'] == currency:
			break 
	#randomly choose a prefix if multiples exist
	prefixes = cur['prefix'].split('|')
	prefix = prefixes[random.randint(0, (len(prefixes)-1))]
	#decrypt the BIP key
	PrivK, Addresshash = bip38.decrypt(str(encrypted_privK), str(passphrase), 8)
	PrivK = enc.decode(PrivK, 256)
	#calculate the address from the key
	publicAddress = address.publicKey2Address(address.privateKey2PublicKey(PrivK), int(cur['version']), prefix, int(cur['length']))
	#check our generated address against the address hash from BIP
	if hashlib.sha256(hashlib.sha256(publicAddress).digest()).digest()[0:4] != Addresshash:
		return False, False
	else:
		return address.privateKey2Wif(PrivK, cur['version'], prefix, cur['length']), publicAddress

def verifyPassword(password):
	"""
		Check the length and complexity of the password
		return true if a pass, false otherwise
	"""
	if len(password) < 7:
		return False
	return True

def vanity(currency, string):
	"""
		Generate a vanity address
	"""
	#using the currencies.json file, get the currency data
	with open('currencies.json', 'r') as dataFile:
		currencies = json.load(dataFile)
	for cur in currencies:
		if cur['currency'] == currency:
			break
	#randomly choose a prefix if multiples exist
	prefixes = cur['prefix'].split('|')
	prefix = prefixes[random.randint(0, (len(prefixes)-1))]
	#generate the private and public keys
	vanityAddress = ''
	while vanityAddress[:(len(string)+1)] != prefix + string:
		privateKey = int(rand.randomKey(random.getrandbits(512)))
		vanityAddress = address.publicKey2Address(address.privateKey2PublicKey(privateKey), int(cur['version']), prefix, int(cur['length']))
		print(vanityAddress)
	print(vanityAddress, privateKey)
	return
