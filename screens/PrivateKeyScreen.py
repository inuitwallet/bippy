from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse

import system.gen as gen
import system.key as key

class PrivateKeyScreen(Screen):
	"""
		Display the actions that work with private keys
	"""

	def __init__(self, BippyApp, **kwargs):
		super(PrivateKeyScreen, self).__init__(**kwargs)

		self.BippyApp = BippyApp

		self.passphrase = StringProperty()
		self.privateKey = StringProperty()
		self.entropy = ListProperty()
		self.newKey = BooleanProperty(False)
		self.isCompressed = True
		self.isBip = BooleanProperty(False)
		self.type = StringProperty()

		#Link to the widgets
		#New Key page
		self.mainLayoutNK = self.ids.mainLayoutNK.__self__
		self.newKeyAccordionItem = self.ids.newKeyAccordionItem.__self__
		self.mainLabelNK = self.ids.mainLabelNK.__self__
		self.passfieldLabelNK = self.ids.passfieldLabelNK.__self__
		self.passfieldNK = self.ids.passfieldNK.__self__
		self.feedbackNK = self.ids.feedbackNK.__self__
		self.checkfieldLabelNK = self.ids.checkfieldLabelNK.__self__
		self.checkfieldNK = self.ids.checkfieldNK.__self__
		self.submitButtonNK = self.ids.submitButtonNK.__self__
		self.encryptButtonNK = self.ids.encryptButtonNK.__self__
		self.progressBarNK = self.ids.progressBarNK.__self__
		self.image = self.ids.image.__self__
		#Existing key page
		self.mainLayoutEK = self.ids.mainLayoutEK.__self__
		self.existingKeyAccordionItem = self.ids.existingKeyAccordionItem.__self__
		self.mainLabelEK = self.ids.mainLabelEK.__self__
		self.privateKeyLabelEK = self.ids.privateKeyLabelEK.__self__
		self.privateKeyInputEK = self.ids.privateKeyInputEK.__self__
		self.passfieldLabelEK = self.ids.passfieldLabelEK.__self__
		self.passfieldEK = self.ids.passfieldEK.__self__
		self.feedbackEK = self.ids.feedbackEK.__self__
		self.checkfieldLabelEK = self.ids.checkfieldLabelEK.__self__
		self.checkfieldEK = self.ids.checkfieldEK.__self__
		self.submitButtonEK = self.ids.submitButtonEK.__self__
		self.actionButtonEK = self.ids.actionButtonEK.__self__

		#remove the widgets that need adding after certain actions.
		#New Key Page
		self.mainLayoutNK.remove_widget(self.submitButtonNK)
		self.mainLayoutNK.remove_widget(self.encryptButtonNK)
		self.mainLayoutNK.remove_widget(self.progressBarNK)
		#Existing Key Page
		self.mainLayoutEK.remove_widget(self.passfieldLabelEK)
		self.mainLayoutEK.remove_widget(self.passfieldEK)
		self.mainLayoutEK.remove_widget(self.feedbackEK)
		self.mainLayoutEK.remove_widget(self.checkfieldLabelEK)
		self.mainLayoutEK.remove_widget(self.checkfieldEK)
		self.mainLayoutEK.remove_widget(self.actionButtonEK)

		self.BippyApp.set_info('Private Key')
		return

	def reset_ui(self, dt):
		"""
			return the UI to it's original state
		"""

		#reset the New Key page
		self.mainLayoutNK.clear_widgets()
		self.mainLabelNK.text = self.BippyApp.get_string('New_Key_Intro_Text')
		self.mainLayoutNK.add_widget(self.mainLabelNK)
		self.mainLayoutNK.add_widget(self.passfieldLabelNK)
		self.passfieldNK.text = ''
		self.mainLayoutNK.add_widget(self.passfieldNK)
		self.feedbackNK.text = ''
		self.mainLayoutNK.add_widget(self.feedbackNK)
		self.mainLayoutNK.add_widget(self.checkfieldLabelNK)
		self.checkfieldNK.text = ''
		self.mainLayoutNK.add_widget(self.checkfieldNK)

		#reset the existing key page
		self.mainLayoutEK.clear_widgets()
		self.mainLabelEK.text = self.BippyApp.get_string('Existing_Key_Intro_Text')
		self.mainLayoutEK.add_widget(self.mainLabelEK)
		self.mainLayoutEK.add_widget(self.privateKeyLabelEK)
		self.privateKeyInputEK.text = ''
		self.mainLayoutEK.add_widget(self.privateKeyInputEK)
		self.mainLayoutEK.add_widget(self.submitButtonEK)
		self.passfieldEK.text = ''
		self.checkfieldEK.text = ''

		#clear parameters
		self.passphrase = ''
		self.privateKey = ''
		self.entropy = []
		self.newKey = False
		self.type = False
		self.isCompressed = True
		self.type = ''

		return

	def check_private_key(self, text):
		"""
			this method is fired when the submit button is pressed
			it checks the format of the entered text and
			ensures that it is a valid private key.
			returns the private key in
		"""
		#Check that a currency has been chosen
		if not self.BippyApp.check_chosen_currency():
			return
		#check if the entered text is a BIP encrypted key
		isBip, comment = key.isBip(text, self.BippyApp.chosenCurrency)
		if isBip is True:
			if comment == 'badchecksum':
				self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Bip_Bad_Checksum'))
				self.privateKeyInputEK.text = ''
				return
			self.mainLabelEK.text = self.BippyApp.get_string('Bip_Key_Entered')
			self.privateKey = text
			self.privateKeyInputEK.text = ''
			self.type = 'BIP'
			self.passphrase_entry()
			return
		#check if it is a compressed or uncompressed WIF key
		isWif, comment = key.isWif(text, self.BippyApp.chosenCurrency)
		if isWif is True:
			if comment == 'badchecksum':
				self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Wif_Bad_Checksum'))
				self.privateKeyInputEK.text = ''
				return
			if comment == 'compressed':
				self.mainLabelEK.text = self.BippyApp.get_string('Compressed_Wif_Key_Entered')
				self.isCompressed = True
			if comment == 'uncompressed':
				self.mainLabelEK.text = self.BippyApp.get_string('Uncompressed_Wif_Key_Entered')
				self.isCompressed = False
			self.privateKey = text
			self.type = 'WIF'
			self.passphrase_entry()
			return
		#check if it's a hex key
		if key.isHex(text) is True:
			self.mainLabelEK.text = self.BippyApp.get_string('Hex_Key_Entered')
			self.privateKey = text
			self.privateKeyInputEK.text = ''
			self.type = 'HEX'
			self.passphrase_entry()
			return
		#check if it's a base64 key
		if key.isBase64(text) is True:
			self.mainLabelEK.text = self.BippyApp.get_string('Base64_Key_Entered')
			self.privateKey = text
			self.privateKeyInputEK.text = ''
			self.type = 'B64'
			self.passphrase_entry()
			return
		#check if it's a base6 key
		if key.isBase6(text) is True:
			self.mainLabelEK.text = self.BippyApp.get_string('Base6_Key_Entered')
			self.privateKey = text
			self.privateKeyInputEK.text = ''
			self.type = 'B6'
			self.passphrase_entry()
			return

		#None of the above rules match so no key has been detected
		self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), self.BippyApp.get_string('Not_Private_Key'))
		self.reset_ui(None)
		return

	def passphrase_entry(self):
		"""
			set up the UI ready for passphrase entry
		"""

		self.mainLayoutEK.remove_widget(self.privateKeyLabelEK)
		self.mainLayoutEK.remove_widget(self.privateKeyInputEK)
		self.mainLayoutEK.remove_widget(self.submitButtonEK)
		self.mainLayoutEK.add_widget(self.passfieldLabelEK)
		self.mainLayoutEK.add_widget(self.passfieldEK)
		self.mainLayoutEK.add_widget(self.feedbackEK)
		self.mainLayoutEK.add_widget(self.checkfieldLabelEK)
		self.mainLayoutEK.add_widget(self.checkfieldEK)
		self.passfieldEK.focus = True
		return

	def set_screen(self):
		"""
			set the info text based on which accordion item is collapsed
		"""
		if self.newKeyAccordionItem.collapse is True:
			self.BippyApp.set_info('Private Key')
		else:
			self.BippyApp.set_info('New Private Key')
		return

	def check_passphrase(self, passfield, checkfield, feedback, layout, button):
		"""
			Check that the entered passphrase confirms to the basic rules
			ialso check that the confirmation matches the original
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
			if self.type == 'BIP':
				button.text = self.BippyApp.get_string('Decrypt')
			else:
				button.text = self.BippyApp.get_string('Encrypt')
			layout.add_widget(button)
			self.passphrase = passphrase
			return

	def submit_passphrase(self):
		"""
			Submit the passwords and move to the next screen
		"""
		if not self.BippyApp.check_chosen_currency():
			return
		#save the passphrase and clear the passphrase boxes
		self.passphrase = self.passfieldNK.text
		self.passfieldNK.text = ''
		self.checkfieldNK.text = ''
		#restructure the UI
		self.mainLayoutNK.remove_widget(self.passfieldLabelNK)
		self.mainLayoutNK.remove_widget(self.passfieldNK)
		self.mainLayoutNK.remove_widget(self.checkfieldLabelNK)
		self.mainLayoutNK.remove_widget(self.checkfieldNK)
		self.mainLayoutNK.remove_widget(self.submitButtonNK)

		self.mainLayoutNK.add_widget(self.progressBarNK)
		#Display instructions to the user
		self.mainLabelNK.text = self.BippyApp.get_string('Entropy_Explanation')
		self.entropy = []
		self.bind(on_touch_move=self.draw_entropy)

	def draw_entropy(self, instance, value=False):
		"""
			This function is enabled when only a password has been entered.
			It allows the user to draw on the image shown to the right of the UI
			This is the method by which entropy is gathered for generation of key pairs
		"""
		with self.canvas:
			Color(0, 0.86667, 1)
			d = 5.
			if self.collide_point(value.x, value.y):
				Ellipse(pos=(value.x - d / 2, value.y - d / 2), size=(d, d), group='ellipses')
				self.entropy.append((int(value.x), int(value.y)))
				self.progressBarNK.value += 1
		if self.progressBarNK.value == 800:
			self.unbind(on_touch_move=self.draw_entropy)
			self.progressBarNK.value = 0
			self.mainLayoutNK.remove_widget(self.progressBarNK)
			self.canvas.remove_group('ellipses')
			self.mainLabelNK.text=self.BippyApp.get_string('Enough_Entropy')
			self.mainLayoutNK.add_widget(self.encryptButtonNK)
			self.newKey = True
			self.type = 'New'
		return

	def action_start(self, layout, label):
		"""
			Start the encryption process
			If we start encryption straight away, the UI doesn't have a chance to update
		"""
		#remove widgets and alert the user to the fact that BIP0038 encryption is starting
		layout.clear_widgets()
		if self.type == 'BIP':
			label.text = self.BippyApp.get_string('Starting_Decryption')
		else:
			label.text = self.BippyApp.get_string('Starting_Bip')
		layout.add_widget(label)

		#use clock to delay the start of the encryption otherwise the message above is never shown
		if self.type == 'BIP':
			Clock.schedule_once(self.decrypt, 0.5)
		else:
			Clock.schedule_once(self.encrypt, 0.5)
		return

	def encrypt(self, dt):
		"""
			Perform the actual encryption
		"""
		self.BippyApp.check_chosen_currency()
		if self.newKey is True:
			BIP, Address = gen.genBIPKey(self.BippyApp.chosenCurrency, self.passphrase, self.entropy, '', self.isCompressed)
		else:
			#otherwise, we encrypt the existing key
			BIP, Address = gen.encBIPKey(self.privateKey, self.BippyApp.chosenCurrency, self.passphrase, self.isCompressed)
		resultsScreen = self.BippyApp.mainScreenManager.get_screen('Results')
		resultsScreen.display_bip(BIP, Address)
		#clear the UI
		Clock.schedule_once(self.reset_ui, 5)
		return

	def decrypt(self, dt):
		"""
			Perform the decryption using the saved details
		"""
		self.BippyApp.check_chosen_currency()
		WIF, Address = gen.decBIPKey(self.privateKey, self.passphrase, self.BippyApp.chosenCurrency)
		resultsScreen = self.BippyApp.mainScreenManager.get_screen('Results')
		resultsScreen.display_wif(WIF, Address)
		#clear the UI
		Clock.schedule_once(self.reset_ui, 5)
		return


