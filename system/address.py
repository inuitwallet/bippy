import hashlib

import num.elip as elip
import num.enc as enc

def privateKey2Wif(privateKey, version=0, prefix=1, length=0, isCompressed=True):
	if isCompressed is True:
		return base58Encode(enc.encode(privateKey, 256, 32) + '\x01', (128+int(version)), prefix, length)
	else:
		return base58Encode(enc.encode(privateKey, 256, 32), (128+int(version)), prefix, length)


def privateKey2PublicKey(priv, isCompressed=True):
	""" integer 256 bit ECC private key to hexstring compressed or uncompressed public key
	"""
	pub = elip.base10_multiply(elip.G, priv)
	if isCompressed is True:
		#starts with 2 or 3 based on whether y is even or not
		return '0' + str(2 + (pub[1] % 2)) + enc.encode(pub[0], 16, 64)
	else:
		#starts with 04 and then x and y
		return '04' + enc.encode(pub[0], 16, 64) + enc.encode(pub[1], 16, 64)


def publicKey2Address(publicKey, version=0, prefix=1, length=0):
	""" Compressed ECC public key hex to address
	"""
	return base58Encode(hashlib.new('ripemd160', hashlib.sha256(publicKey.decode('hex')).digest()).digest(), (0+int(version)), prefix, length)


def base58Encode(r160, magicbyte=0, prefix=1, length=0):
	""" Base58 encoding w leading zero compact
	"""
	from re import match as re_match
	inp_fmtd = chr(int(magicbyte if magicbyte < 255 else 255)) + r160
	leadingzbytes = len(re_match('^\x00*', inp_fmtd).group(0))
	checksum = hashlib.sha256(hashlib.sha256(inp_fmtd).digest()).digest()[:4]
	return str(prefix) * leadingzbytes + enc.encode(enc.decode(inp_fmtd + checksum, 256), 58, 0)
