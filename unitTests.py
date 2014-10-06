import system.gen as gen
import random
import json
import encrypt.electrum as electrum

def End2End(cur):
	"""
		Generate a BIP key using random entropy each time
		Decrypt BIP Key to get compressed WIF Key
		Encrypt WIF Key to test that same BIP Key is generated.
		Also check the generated public address at each stage
	"""
	#build the entropy
	entropy = []
	count = 0
	while count <= 52:
		count+=1
		entropy.append((int(random.getrandbits(52)),int(random.getrandbits(52))))
	#generate a BIP key and address using the entropy above
	BIP_1, publicAddress_1 = gen.genBIPKey(cur, 'End2EndTest', entropy)
	#decrypt the BIP key to give a WIF key and address
	WIF, publicAddress_2 = gen.decBIPKey(BIP_1, 'End2EndTest', cur)
	#encrypt the WIF key to give a BIP Key and address
	BIP_2, publicAddress_3 = gen.encBIPKey(WIF, cur, 'End2EndTest')
	#chekc that the BIP Keys are the same
	if BIP_1 != BIP_2:
		print(cur + ' BIP Keys do not match\n' + BIP_1 + ' != ' + BIP_2)
		return False
	#check that the public keys are the same
	if publicAddress_1 != publicAddress_2 != publicAddress_3:
		print(cur + ' public addresses do not match\n' + publicAddress_1 + ' != ' + publicAddress_2 + ' != ' + publicAddress_3)
		return False
	return True

def encryptKnown(cur):
	"""
		Using known good keys, encrypt and then decrypt to check the results
		The good keys were all exported from the specified currencies default QT wallet
	"""
	#fetch the known key details for the chosen currency
	keys = json.load(open('res/json/unitTestKeys.json', 'r'))
	for key in keys:
		if key['currency'] == cur:
			break
	#check that the end of the list wasn't reached due to un-found keys
	if key['currency'] != cur or key['privK'] == '':
		print('No key details found for ' + cur)
		return False
	#encrypt the WIF privateKey
	BIP_1, publicAddress_1 = gen.encBIPKey(key['privK'], cur, 'encryptKnownTest')
	#decrypt the BIP key to produce a WIF Key and Address
	WIF_1, publicAddress_2 = gen.decBIPKey(BIP_1, 'encryptKnownTest', cur)
	#check that the saved BIP key and generated BIP key are the same
	if BIP_1 != key['bip']:
		print(cur + ' BIP Keys do not match\n' + BIP_1 + ' != ' + key['bip'])
		return False
	#check that the decrypted WIF key is the same as the known WIF key
	if WIF_1 != key['privK']:
		print(cur + ' the WIF Private Keys do not match\n' + WIF_1 + ' != ' + key['privK'])
		return False
	#check that the addresses are the same
	if publicAddress_1 != publicAddress_2 != key['address']:
		print(cur + ' public addresses do not match\n' + publicAddress_1 + ' != ' + publicAddress_2 + ' != ' + key['address'])
		return False
	return True

def electrumTest():
	"""
		Generate a random Electrum seeds and then encrypt and decrypt them
	"""
	seed = electrum.buildRandom()
	print(seed)
	enc = electrum.encrypt(seed, 'thisisatest')
	dec = electrum.decrypt(enc, 'thisisatest')
	if seed != dec:
		print('The decrypted seed doesn\'t match the original')
		return False
	return True

if __name__ == '__main__':
	#get the list of currencies
	with open('res/json/currencies.json', 'r') as dataFile:
		currencies = json.load(dataFile)

	failCount = 0
	goodCount = 0

	#show the intro text
	print('')
	print('===============================')
	print('Welcome to the bippy test suite')
	print('===============================')
	print('')
	print('The first test will generate 3 random private keys for each currency.')
	print('Each key will be BIP0038 encrypted and then decrypted.')
	print('The results will be checked for consistency.')
	cont = raw_input('Do you want to continue? (y) : ')

	if cont != 'n':
		#run end to end test
		for cur in currencies:
			count = 0
			print(cur['longName'])
			while count < 3:
				count += 1
				print(count)
				if End2End(cur['currency']) is False:
					failCount += 1
				else:
					goodCount += 1

	print('The next test will use a list of known private key and address details.')
	print('These details were all exported from the currencies default QT wallet.')
	print('The test will BIP0038 encrypt and decrypt the known keys and then check for consistency.')
	cont = raw_input('Do you want to continue? (y) : ')

	if cont != 'n':
		#run the knownKey test
		for cur in currencies:
			print(cur['longName'])
			if encryptKnown(cur['currency']) is False:
				failCount += 1
			else:
				goodCount += 1

	print('The next test will use generate 50 random Electrum seeds.')
	print('These will be encrypted and then decrypted to test for consistency.')
	cont = raw_input('Do you want to continue? (y) : ')

	if cont != 'n':
		#run the Electrum test
		for x in xrange(0,50):
			if electrumTest() is False:
				failCount += 1
			else:
				goodCount += 1

	print('')
	print('===============================')
	print('Results')
	print('===============================')
	print('')
	print(str(failCount+goodCount) + ' tests were performed.')
	print(str(goodCount) + ' tests passed.')
	print(str(failCount) + ' tests failed.')
	print('')
	if failCount > 0:
		print('You may want to contact the creators of bippy to find out why the tests failed.')
	else:
		print('All tests passed! bippy seems to work on your machine.')
