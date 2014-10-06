from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import system.key as key
import encrypt.electrum as electrum
import time


class MnemonicSeedScreen(Screen):
	"""
		The Mnemonic Seed Encryption / Decryption Screen
	"""

	def __init__(self, BippyApp, **kwargs):
		super(MnemonicSeedScreen, self).__init__(**kwargs)
		self.BippyApp = BippyApp

		self.mainLayout = self.ids.mainLayout.__self__
		self.mainLabel = self.ids.mainLabel.__self__
		self.seedLabel = self.ids.seedLabel.__self__
		self.seedfield = self.ids.seedfield.__self__
		self.submitButton = self.ids.submitButton.__self__
		self.passfieldLabel = self.ids.passfieldLabel.__self__
		self.passfield = self.ids.passfield.__self__
		self.feedback = self.ids.feedback.__self__
		self.checkfieldLabel = self.ids.checkfieldLabel.__self__
		self.checkfield = self.ids.checkfield.__self__
		self.encryptButton = self.ids.encryptButton.__self__

		#set up the page for seed collection
		self.mainLayout.remove_widget(self.passfieldLabel)
		self.mainLayout.remove_widget(self.passfield)
		self.mainLayout.remove_widget(self.feedback)
		self.mainLayout.remove_widget(self.checkfieldLabel)
		self.mainLayout.remove_widget(self.checkfield)
		self.mainLayout.remove_widget(self.encryptButton)

		self.type = None
		self.seed = ''
		self.passphrase = ''
		return

	def reset_ui(self, dt):
		"""
			return the UI to it's original state
		"""

		#reset the New Key page
		self.mainLayout.clear_widgets()
		self.mainLabel.text = self.BippyApp.get_string('Mnemonic_Intro_Text')
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.seedLabel)
		self.seedfield.text = ''
		self.mainLayout.add_widget(self.seedfield)
		self.mainLayout.add_widget(self.submitButton)

		#clear passphrase fields
		self.passfield.text = ''
		self.checkfield.text = ''

		#clear parameters
		self.passphrase = ''
		self.seed = ''
		self.type = None
		return

	def submit_seed(self):
		"""
			check that the supplied text is a valid Electrum Seed
		"""
		seed = self.seedfield.text

		#check if seed is a valid electrum seed
		isSeed, comment = key.isElectrumSeed(seed)
		if isSeed is True:
			if comment == 'invalid word':
				self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Invalid_Word_Electrum_Seed'))
				return
			self.mainLabel.text = self.BippyApp.get_string('Valid_Electrum_Seed')
			self.passphrase_entry()
			self.seed = self.seedfield.text
			self.type = 'Electrum Seed'
			return
		#see if it's an encrypted electrum seed
		isEncElectrumSeed, comment = key.isEncElectrumSeed(seed)
		if isEncElectrumSeed is True:
			if comment == 'checksum':
				self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Encrypted_Electrum_Bad_Checksum'))
				return
			self.mainLabel.text = self.BippyApp.get_string('Valid_Encrypted_Electrum_Seed')
			self.passphrase_entry()
			self.seed = self.seedfield.text
			self.type = 'Encrypted Electrum Seed'
			return

		#if we get here, no valid seed or encrypted seed was detected
		self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Not_Mnemonic_Seed'))
		self.reset_ui(None)
		return

	def passphrase_entry(self):
		"""
			Set up the UI ready for passphrase entry
		"""
		self.mainLayout.clear_widgets()
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.passfieldLabel)
		self.mainLayout.add_widget(self.passfield)
		self.mainLayout.add_widget(self.feedback)
		self.mainLayout.add_widget(self.checkfieldLabel)
		self.mainLayout.add_widget(self.checkfield)
		return

	def check_passphrase(self, passfield, checkfield, feedback, layout, button):
		"""
			Check that the entered passphrase confirms to the basic rules
			also check that the confirmation matches the original
		"""

		layout.remove_widget(button)
		if self.type == 'Electrum Seed':
			button.text = 'Encrypt'
		if self.type == 'Encrypted Electrum Seed':
			button.text = 'Decrypt'

		#get the text we need to compare
		passphrase = passfield.text
		checktext = checkfield.text

		#check for tabs in the passphrase or check string.
		#tabs don't do anything as standard so we check for them and move the focus accordingly
		if '\t' in passphrase:
			passfield.text = passphrase.replace('\t','')
			checkfield.focus = True
			return
		if '\t' in checktext:
			checkfield.text = checktext.replace('\t','')
			passfield.focus = True
			return

		#check the passphrase against the rules
		if len(passphrase) < 1:
			feedback.text = ''
			return
		if 7 > len(passphrase) > 0:
			feedback.color = (1,0,0,1)
			feedback.text = self.BippyApp.get_string('Passphrase_Too_Short')
			return
		elif passphrase != checktext:
			feedback.color = (1,0.3,0,1)
			feedback.text = self.BippyApp.get_string('Passphrases_Dont_Match')
			return
		else:
			feedback.text = ''
			layout.add_widget(button)
			self.passphrase = passphrase
			return

	def action_start(self, layout, label):
		"""
			Start the encryption process
			If we start encryption straight away, the UI doesn't have a chance to update
		"""
		#remove widgets and alert the user to the fact that BIP0038 encryption is starting
		layout.clear_widgets()
		if self.type == 'Electrum Seed':
			label.text = self.BippyApp.get_string('Starting_Bip')
		if self.type == 'Encrypted Electrum Seed':
			label.text = self.BippyApp.get_string('Starting_Decryption')
		layout.add_widget(label)

		#use clock to delay the start of the encryption otherwise the message above is never shown
		if self.type == 'Electrum Seed':
			Clock.schedule_once(self.encrypt, 0.5)
		if self.type == 'Encrypted Electrum Seed':
			Clock.schedule_once(self.decrypt, 0.5)
		return

	def encrypt(self, dt):
		"""
			Perform the actual encryption
		"""
		resultsScreen = self.BippyApp.mainScreenManager.get_screen(self.BippyApp.get_string('Results_Screen'))

		if self.type == 'Electrum Seed':
			eBIP = electrum.encrypt(self.seed, self.passphrase)
			resultsScreen.display_bip_mnemonic(eBIP, 'Electrum')

		#clear the UI
		Clock.schedule_once(self.reset_ui, 5)
		return

	def decrypt(self, dt):
		"""
			perform the decryption
		"""
		resultsScreen = self.BippyApp.mainScreenManager.get_screen(self.BippyApp.get_string('Results_Screen'))
		if self.type == 'Encrypted Electrum Seed':
			seed, message = electrum.decrypt(self.seed, self.passphrase)
			if seed is False:
				if message == 'checksum':
					self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Encrypted_Electrum_Bad_Checksum'))
					return
				if message == 'salt':
					self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string(''))
			else:
				resultsScreen.display_mnemonic(seed, 'Electrum')
