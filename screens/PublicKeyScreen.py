from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import system.key as key
import encrypt.public_address as pub_address


class PublicKeyScreen(Screen):
	"""
		Display the actions that work with public keys
	"""

	def __init__(self, BippyApp, **kwargs):
		super(PublicKeyScreen, self).__init__(**kwargs)

		self.BippyApp = BippyApp

		self.pub_address = ''
		self.type = ''
		self.passphrase = ''

		self.mainLayout = self.ids.mainLayout.__self__
		self.mainLabel = self.ids.mainLabel.__self__
		self.keyLabel = self.ids.keyLabel.__self__
		self.keyfield = self.ids.keyfield.__self__
		self.submitButton = self.ids.submitButton.__self__

		self.passfieldLabel = self.ids.passfieldLabel.__self__
		self.passfield = self.ids.passfield.__self__
		self.feedback = self.ids.feedback.__self__
		self.checkfieldLabel = self.ids.checkfieldLabel.__self__
		self.checkfield = self.ids.checkfield.__self__
		self.encryptButton = self.ids.encryptButton.__self__

		#set up ui for first display
		self.reset_ui(None)

		return

	def reset_ui(self, dt):
		"""
			set the UI for first use
		"""
		#set up ui for first display
		self.mainLayout.clear_widgets()
		self.mainLabel.text = self.BippyApp.get_string('Public_Key_Intro_Text')
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.keyLabel)
		self.mainLayout.add_widget(self.keyfield)
		self.mainLayout.add_widget(self.submitButton)

		self.pub_address = ''
		self.type = ''
		self.passphrase = ''
		return

	def check_address(self, text):
		"""
			this method is fired when the submit button is pressed
			it checks the format of the entered text and
			ensures that it is a valid public address.
		"""
		#Check that a currency has been chosen
		if not self.BippyApp.check_chosen_currency():
			return

		#see if the entered text is a valid address
		isAddress, comment = key.isAddress(text, self.BippyApp.chosenCurrency)
		if isAddress is True:
			#alert the user to the error
			if comment == 'checksum':
				self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Address_Bad_Checksum'))
				return
			if comment == 'prefix':
				self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Not_Valid_Address') + ' ' + self.BippyApp.chosenCurrencyLongName + ' ' + self.BippyApp.get_string('Address'))
				return
			self.pub_address = self.keyfield.text
			self.type = 'address'
			self.passphrase_entry()
			self.mainLabel.text = self.BippyApp.get_string('Valid_Public_Address_1') + self.BippyApp.chosenCurrencyLongName + ' ' + self.BippyApp.get_string('Address') + self.BippyApp.get_string('Valid_Public_Address_2')
			return

		#check if the entered text is an encrypted address
		isEncAddress, comment = key.isEncAddress(text)
		if isEncAddress is True:
			if comment == 'checksum':
				self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Encrypted_Address_Bad_Checksum'))
				return
			self.pub_address = self.keyfield.text
			self.type = 'encaddress'
			self.passphrase_entry()
			self.mainLabel.text = self.BippyApp.get_string('Valid_Encrypted_Address')
			return

		#if we get here, no valid string has been displayed
		self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('No_Valid_Address'))
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
			if self.type == 'address':
				button.text = self.BippyApp.get_string('Encrypt')
			if self.type == 'encaddress':
				button.text = self.BippyApp.get_string('Decrypt')
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
		if self.type == 'address':
			label.text = self.BippyApp.get_string('Starting_Bip')
		if self.type == 'encaddress':
			label.text = self.BippyApp.get_string('Starting_Decryption')
		layout.add_widget(label)

		#use clock to delay the start of the encryption otherwise the message above is never shown
		if self.type == 'address':
			Clock.schedule_once(self.encrypt, 0.5)
		if self.type == 'encaddress':
			Clock.schedule_once(self.decrypt, 0.5)
		return

	def encrypt(self, dt):
		"""
			Perform the actual encryption
		"""
		self.BippyApp.check_chosen_currency()
		resultsScreen = self.BippyApp.mainScreenManager.get_screen(self.BippyApp.get_string('Results_Screen'))

		eAdd = pub_address.encrypt(self.pub_address, self.passphrase)
		resultsScreen.display_bip_pub_address(eAdd)

		#clear the UI
		Clock.schedule_once(self.reset_ui, 5)
		return

	def decrypt(self, dt):
		"""
			Perform the actual encryption
		"""
		self.BippyApp.check_chosen_currency()

		add, comment = pub_address.decrypt(self.pub_address, self.passphrase)
		#address only returned
		if add is True:
			resultsScreen = self.BippyApp.mainScreenManager.get_screen(self.BippyApp.get_string('Results_Screen'))
			resultsScreen.display_pub_address(comment)
		else:
			if comment == 'checksum':
				self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Encrypted_Address_Bad_Checksum'))
			if comment == 'salt':
				self.BippyApp.show_popup(self.BippyApp.get_atring('Popup_Error'), self.BippyApp.get_string('Encrypted_Address_No_Match'))

		#clear the UI
		Clock.schedule_once(self.reset_ui, 5)
		return
