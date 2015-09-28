from kivy.uix.screenmanager import Screen

class LinksScreen(Screen):
	"""
		Display WoodWallets links to the user on request
	"""

	def __init__(self, BippyApp, **kwargs):
		super(LinksScreen, self).__init__(**kwargs)
		self.BippyApp = BippyApp

		self.linkAccordion = self.ids.linkAccordion.__self__

		self.public = self.ids.public.__self__
		self.publicImage = self.ids.publicImage.__self__
		self.publicUrl = self.ids.publicUrl.__self__

		self.private = self.ids.private.__self__
		self.privateImage = self.ids.privateImage.__self__
		self.privateUrl = self.ids.privateUrl.__self__

		self.double = self.ids.double.__self__
		self.doubleImage = self.ids.doubleImage.__self__
		self.doubleUrl = self.ids.doubleUrl.__self__

	def reset_ui(self, dt):
		"""
			clear all text from the ui
		"""
		self.publicUrl.text = ''
		self.privateUrl.text = ''
		self.doubleUrl.text = ''
		return

	def get_public_ww(self, public):
		"""
			return the Woodwallets url for public key only
		"""
		return 'https://woodwallets.io/product/woodwallet-public-address?pub_addr={}&' \
			   'pub_coin={}&orig=bipppy'.format(public,
												self.BippyApp.chosenCurrencyLongName)

	def get_private_ww(self, private, mnemonic=''):
		"""
			return the Woodwallets url for private key only
		"""
		if mnemonic == '':
			coin = self.BippyApp.chosenCurrencyLongName
		else:
			coin = mnemonic
		return 'https://woodwallets.io/product/one-side-private-key-only?pvt_pvtkey={}&' \
			   'pvt_coin={}&orig=bippy'.format(private, coin)

	def get_double_ww(self, public, private):
		"""
			return the double sided url for both private key and public address
		"""
		return 'https://woodwallets.io/product/woodwallet-private-key-and-public-address' \
			   '?dbl_addr={}&dbl_pvtkey={}&dbl_coin={}&orig=bippy'.format(public,
																		  private,
																		  self.BippyApp.chosenCurrencyLongName)
