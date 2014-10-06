import encrypt.scrypt as scrypt
import encrypt.aes as aes
import num.enc as enc
import hashlib
import math

def encrypt(pub_address, passphrase):
	"""
		Encrypt the public address
	"""

	#1 base 58 decode the public address
	address = enc.b58decode(pub_address)

	#2. Take a hash of the decoded address to act as a scrypt salt
	salt = hashlib.sha256(hashlib.sha256(address).digest()).digest()[:4]

	#2. Derive a key from the passphrase using scrypt
	key = scrypt.hash(passphrase, salt, 16384, 8, 8)

	#3. Split the key into half 1 and half 2
	derivedhalf1 = key[0:32]
	derivedhalf2 = key[32:64]

	#4 AES encrypt address halves as per bip38
	halflength = int(math.floor(len(address) / 2))
	Aes = aes.Aes(derivedhalf2)
	#for Aes encryption, string needs to have length = 16
	xorhalf1 = enc.sxor(address[:halflength], derivedhalf1[:16]).ljust(16, '0')
	xorhalf2 = enc.sxor(address[halflength:], derivedhalf1[16:32]).ljust(16, '0')
	encryptedhalf1 = Aes.enc(xorhalf1)
	encryptedhalf2 = Aes.enc(xorhalf2)

	#5. The encrypted private key is the Base58Check-encoded concatenation of the following
	# \x78\x8e\xa3\x69\xb6 + address_length + salt + encryptedhalf1 + encryptedhalf2
	encAddress = '\x78\x8e\xa3\x69\xb6' + chr(len(address)) + salt + encryptedhalf1 + encryptedhalf2
	check = hashlib.sha256(hashlib.sha256(encAddress).digest()).digest()[:4]
	return enc.b58encode(encAddress + check)

def decrypt(enc_address, passphrase):
	"""
		Decrypt an Public Address encrypted with the above method
	"""
	#1. Base 58 decrypt the encrypted key
	# get the two encrypted halves, the check and the salt
	dec_address = enc.b58decode(enc_address)
	check = dec_address[-4:]
	#check that it's not been tampered with
	if check != hashlib.sha256(hashlib.sha256(dec_address[:-4]).digest()).digest()[:4]:
		return False, 'checksum'

	length = ord(dec_address[5:6])
	halflength = int(math.floor(length / 2))
	salt = dec_address[6:10]
	encryptedhalfs = dec_address[10:len(dec_address) - 4]
	encryptedhalf1 = encryptedhalfs[:16]
	encryptedhalf2 = encryptedhalfs[16:]

	#2. Derive the decryption key using scrypt
	key = scrypt.hash(passphrase, salt, 16384, 8, 8)
	derivedhalf1 = key[0:32]
	derivedhalf2 = key[32:64]

	#3. Aes decrypt the encrypted halves
	Aes = aes.Aes(derivedhalf2)
	xorhalf1 = Aes.dec(encryptedhalf1)
	xorhalf2 = Aes.dec(encryptedhalf2)

	#4 . xor them with the two halves of derivedhalf1 to get the original values
	half1 = enc.sxor(xorhalf1[:halflength], derivedhalf1[:16])
	half2 = enc.sxor(xorhalf2[:(length - halflength)], derivedhalf1[16:32])

	#5. build the address and check it against the check hash
	pub_address = half1 + half2
	if salt != hashlib.sha256(hashlib.sha256(pub_address).digest()).digest()[:4]:
		return False, 'salt'

	#6. return the address as a single string
	return True, enc.b58encode(pub_address)
