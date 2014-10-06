from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.clock import Clock


class ResultsScreen(Screen):
	"""
		The screen that displays the results to the user
	"""

	def __init__(self, BippyApp, **kwargs):
		super(ResultsScreen, self).__init__(**kwargs)
		self.BippyApp = BippyApp

		self.mainLayout = self.ids.mainLayout.__self__
		self.mainLabel = self.ids.mainLabel.__self__
		self.topLabel = self.ids.topLabel.__self__
		self.topField = self.ids.topField.__self__
		self.middleLabel = self.ids.middleLabel.__self__
		self.middleField = self.ids.middleField.__self__
		self.middleFieldMulti = self.ids.middleFieldMulti.__self__
		self.bottomLabel = self.ids.bottomLabel.__self__
		self.bottomField = self.ids.bottomField.__self__
		return

	def switch_to_results(self, dt):
		"""
			switch to the results screen
		"""
		self.BippyApp.mainScreenManager.transition = SlideTransition(direction='right')
		self.BippyApp.mainScreenManager.current = self.BippyApp.get_string('Results_Screen')
		return

	def display_bip(self, BIP, Address):
		"""
			Display the BIP encrypted key, the address and the links
		"""
		self.mainLayout.clear_widgets()
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.topLabel)
		self.mainLayout.add_widget(self.topField)
		self.mainLayout.add_widget(self.bottomLabel)
		self.mainLayout.add_widget(self.bottomField)

		Clock.schedule_once(self.switch_to_results, 0.5)

		self.mainLabel.text = self.BippyApp.get_string('Bip_Successful')
		self.topLabel.text = self.BippyApp.get_string('Bip_Key_Label')
		self.topField.text = str(BIP)
		self.bottomLabel.text = self.BippyApp.get_string('Address_Label')
		self.bottomField.text = str(Address)
		self.canvas.ask_update()
		return

	def display_wif(self, WIF, Address):
		"""
			Display the decrypted WIF key, the address and the links
		"""
		self.mainLayout.clear_widgets()
		self.mainLayout.add_widget(self.mainLabel)

		if WIF is False or Address is False:
			self.mainLabel.text = self.BippyApp.get_string('Bip_Decrypt_Unsuccessful')
			return

		self.mainLayout.add_widget(self.topLabel)
		self.mainLayout.add_widget(self.topField)
		self.mainLayout.add_widget(self.bottomLabel)
		self.mainLayout.add_widget(self.bottomField)

		Clock.schedule_once(self.switch_to_results, 0.5)

		self.mainLabel.text = self.BippyApp.get_string('Bip_Decrypt_Successful')
		self.topLabel.text = self.BippyApp.get_string('Wif_Key_Label')
		self.topField.text = str(WIF)
		self.bottomLabel.text = self.BippyApp.get_string('Address_Label')
		self.bottomField.text = str(Address)
		self.canvas.ask_update()
		return

	def display_bip_mnemonic(self, sBIP, type):
		"""
			Display the BIP encrypted mnemonic seed
		"""
		self.mainLayout.clear_widgets()
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.middleLabel)
		self.mainLayout.add_widget(self.middleField)

		Clock.schedule_once(self.switch_to_results, 0.5)

		if type == 'Electrum':
			self.mainLabel.text = self.BippyApp.get_string('Electrum_Encrypt_Successful')
			self.middleLabel.text = self.BippyApp.get_string('Electrum_Encrypted_Label')
		self.middleField.text = str(sBIP)
		self.canvas.ask_update()
		return

	def display_mnemonic(self, seed, type):
		"""
			Display the decrypted Mnemonic seed
		"""
		self.mainLayout.clear_widgets()
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.middleLabel)
		self.mainLayout.add_widget(self.middleFieldMulti)

		Clock.schedule_once(self.switch_to_results, 0.5)

		if type == 'Electrum':
			self.mainLabel.text = self.BippyApp.get_string('Electrum_Decrypt_Successful')
			self.middleLabel.text = self.BippyApp.get_string('Electrum_Label')
		self.middleFieldMulti.text = str(seed)
		self.canvas_ask_update()
		return

	def display_bip_pub_address(self, encAddress):
		"""
			Display the newly encrypted public address
		"""
		self.mainLayout.clear_widgets()
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.middleLabel)
		self.mainLayout.add_widget(self.middleField)
		
		Clock.schedule_once(self.switch_to_results, 0.5)
		
		self.mainLabel.text = self.BippyApp.get_string('Address_Encryption_Successful')
		self.middleLabel.text = self.BippyApp.get_string('Encrypted_Address_Label')
		self.middleField.text = str(encAddress)
		self.canvas.ask_update()
		return

	def display_pub_address(self, Address):
		"""
			Display the decrypted public Address
		"""
		self.mainLayout.clear_widgets()
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.middleLabel)
		self.mainLayout.add_widget(self.middleField)

		Clock.schedule_once(self.switch_to_results, 0.5)

		self.mainLabel.text = self.BippyApp.get_string('Address_Decryption_Successful')
		self.middleLabel.text = self.BippyApp.get_string('Address_Label')
		self.middleField.text = str(Address)
		self.canvas.ask_update()
		return
		
		

