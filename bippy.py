"""
	bippy.
	Simple tool for enabling BIP 38 encryption of a variety of crypto-currency private keys

	Sponsored by http://woodwallets.io
	Written by the creator of inuit (http://inuit-wallet.co.uk)
"""

from kivy.config import Config, ConfigParser
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '400')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'fullscreen', '0')
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.uix.settings import Settings
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager
from kivy.animation import Animation
from kivy.uix.actionbar import ActionBar
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.popup import Popup
from kivy.lang import Builder

import json

#import the screens
import screens.HomeScreen as HomeScreen
import screens.ResultsScreen as ResultsScreen
import screens.LinksScreen as LinksScreen
import screens.PrivateKeyScreen as PrivateKeyScreen
import screens.MnemonicSeedScreen as MnemonicSeedScreen
import screens.IntermediateCodeScreen as IntermediateCodeScreen
import screens.PublicKeyScreen as PublicKeyScreen
import screens.VanityScreen as VanityScreen


class TopActionBar(ActionBar):
	"""
		The top Action Bar
	"""

	def __init__(self, BippyApp, **kwargs):
		super(TopActionBar, self).__init__(**kwargs)

		self.BippyApp = BippyApp

		self.topActionView = self.ids.topActionView.__self__
		self.topActionPrevious = self.ids.topActionPrevious.__self__
		self.currencySpinner = self.ids.currencySpinner.__self__
		self.actionSpinner = self.ids.actionSpinner.__self__
		return

	def switch_screen(self, screen):
		"""
			This method is fired whenever a new function is selected in the functions dropdown
			It's job is to set the current screen in the screen manager and set the status of the top action bar
		"""
		#When we reset the function bar text as it fires this routine.
		#catch that here
		if screen == self.BippyApp.get_string('Action_Title'):
			return

		#set the state of the top bar according to the screen that has been requested
		self.topActionPrevious.with_previous = False if screen == self.BippyApp.get_string('Home_Screen') else True

		#currencies are not important to Mnemonic encryption disable the currency spinner
		if screen == self.BippyApp.get_string('Mnemonic_Seed_Screen'):
			self.set_currency(self.BippyApp.get_string('No_Currency_Selected'))
			self.currencySpinner.disabled = True
		else:
			self.set_currency(self.ids.currencySpinner.text)
			self.currencySpinner.disabled = False

		#the Action spinner always shows the choose action instruction
		self.actionSpinner.text = self.BippyApp.get_string('Action_Title')

		#set the transition based on the chosen screen
		self.BippyApp.mainScreenManager.transition = SlideTransition(direction='left') if screen != self.BippyApp.get_string('Home_Screen') else SlideTransition(direction='right')

		#close the info window if it is open before choosing a new screen
		if self.BippyApp.show_info is True:
			self.BippyApp.toggle_info()

		#set the info to display the info for the chosen screen
		self.BippyApp.set_info(screen)

		#set the screen
		self.BippyApp.mainScreenManager.current = screen

		#set the title based on the chosen screen
		self.topActionPrevious.title = self.BippyApp.get_string('Main_Title') + ' - ' + screen if screen != self.BippyApp.get_string('Home_Screen') else self.BippyApp.get_string('Main_Title')

		#chosing the home screen resets the UI
		if screen == self.BippyApp.get_string('Home_Screen'):
			self.BippyApp.reset_ui()

		#set which widget has focus based on the screen that is chosen
		if screen == self.BippyApp.get_string('Private_Key_Screen'):
			if self.BippyApp.privateKeyScreen.newKeyAccordionItem.collapse is True:
				self.BippyApp.privateKeyScreen.privateKeyInputEK.focus = True
			else:
				self.BippyApp.privateKeyScreen.passfieldNK.focus = True
		if screen == self.BippyApp.get_string('Mnemonic_Seed_Screen'):
			self.BippyApp.mnemonicSeedScreen.seedfield.focus = True
		if screen == self.BippyApp.get_string('Public_Key_Screen'):
			self.BippyApp.publicKeyScreen.keyfield.focus = True
		return

	def set_currency(self, currencyLongName):
		"""
			This is fired when a currency is chosen in the dropdown
		"""
		if currencyLongName == self.BippyApp.get_string('No_Currency_Selected'):
			self.BippyApp.chosenCurrency = ''
			self.topActionPrevious.app_icon = 'data/logo/kivy-icon-32.png'
			return
		self.BippyApp.chosenCurrency = self.BippyApp.get_currency_code(currencyLongName)
		self.BippyApp.chosenCurrencyLongName = currencyLongName
		self.topActionPrevious.app_icon = 'res/icons/' + self.BippyApp.chosenCurrency.lower() + '.png'
		self.currencySpinner.text = currencyLongName


class BippyApp(App):
	"""
		The application Class for Bippy
	"""

	def __init__(self, **kwargs):
		super(BippyApp, self).__init__(**kwargs)
		self.isPopup = False
		self.show_info = False

		self.use_kivy_settings = False

		#load config file
		#we don't display the settings panel, changes can be made manually to the ini file
		self.config = ConfigParser()
		self.config.read('bippy.ini')

		self.chosenCurrency = ''
		self.chosenCurrencyLongName = ''
		#load the currencies.json file into memory
		self.currencies = json.load(open('res/json/currencies.json', 'r'))
		#This is the list of available currencies
		self.currencyLongNamesList = ['Bitcoin', 'Litecoin', 'Dogecoin', 'Peercoin', 'Blackcoin', 'Vertcoin']

		#Set the language and load the language file
		self.language = self.config.get('Language', 'active_language')
		try:
			self.lang = json.load(open('res/json/languages/' + self.language + '.json', 'r'))
		except ValueError as e:
			print('')
			print('##################################################################')
			print('')
			print('There was an Error loading the ' + self.language + ' language file.')
			print('')
			print(str(e))
			print('')
			print('##################################################################')
			raise SystemExit
		return

	def build(self):
		"""
			Build the Main Application Window
		"""
		#Root widget is a Box Layout
		self.root = BoxLayout(orientation='vertical')

		self.infoText = TextInput(readonly=True)
		self.mainScreenManager = ScreenManager(transition=SlideTransition(direction='left'))

		#Add the Action Bar
		self.topActionBar = TopActionBar(self)
		self.root.add_widget(self.topActionBar)

		#Add the Scroll View For displaying Info
		self.infoScrollView = ScrollView(size_hint_y=None, height=0, border=1)
		self.infoScrollView.add_widget(self.infoText)
		#self.root.add_widget(self.infoScrollView)

		#Add the screenManager for handling the different screens
		Builder.load_file('screens/HomeScreen.kv')
		self.homeScreen = HomeScreen.HomeScreen(self)
		Builder.load_file('screens/PrivateKeyScreen.kv')
		self.privateKeyScreen = PrivateKeyScreen.PrivateKeyScreen(self)
		Builder.load_file('screens/IntermediateCodeScreen.kv')
		self.intermediateCodeScreen = IntermediateCodeScreen.IntermediateCodeScreen(self)
		Builder.load_file('screens/MnemonicSeedScreen.kv')
		self.mnemonicSeedScreen = MnemonicSeedScreen.MnemonicSeedScreen(self)
		Builder.load_file('screens/PublicKeyScreen.kv')
		self.publicKeyScreen = PublicKeyScreen.PublicKeyScreen(self)
		Builder.load_file('screens/VanityScreen.kv')
		self.vanityScreen = VanityScreen.VanityScreen(self)
		Builder.load_file('screens/ResultsScreen.kv')
		self.resultsScreen = ResultsScreen.ResultsScreen(self)
		Builder.load_file('screens/LinksScreen.kv')
		self.linksScreenWoodWallets = LinksScreen.LinksScreen(self, name=self.get_string('Links_Screen_Wood_Wallets'))

		#Add the screens to the screen manager
		self.mainScreenManager.add_widget(self.homeScreen)
		self.mainScreenManager.add_widget(self.privateKeyScreen)
		self.mainScreenManager.add_widget(self.intermediateCodeScreen)
		self.mainScreenManager.add_widget(self.mnemonicSeedScreen)
		self.mainScreenManager.add_widget(self.publicKeyScreen)
		self.mainScreenManager.add_widget(self.vanityScreen)
		self.mainScreenManager.add_widget(self.resultsScreen)
		self.mainScreenManager.add_widget(self.linksScreenWoodWallets)

		#add the screenmanager to the root
		self.root.add_widget(self.mainScreenManager)

		return self.root

	def check_chosen_currency(self):
		"""
			check that the chosen currency is set.
			display a popup to alert the user if the currency isn't set
		"""
		if self.isPopup is True:
			return
		if self.chosenCurrency is None or self.chosenCurrency == '':
			self.show_popup(self.get_string('No_Currency_Selected'), self.get_string('No_Chosen_Currency'))
			return False
		return True

	def get_currency_code(self, currencyLongName):
		"""
			For the given currency long name return the currency abbreviation
		"""
		for cur in self.currencies:
			if cur['longName'] == currencyLongName:
				return cur['currency']

	def set_info(self, screen):
		"""
			Read the info from the <language>.json file and set it as the info text
		"""
		screenName = None
		for k, v in self.lang.iteritems():
			if v == screen:
				if 'Screen' not in k or 'Screen_Info' in k:
					continue
				screenName = k
				break
		if screenName is not None:
			self.infoText.text = self.get_string(screenName + '_Info')

	def toggle_info(self):
		"""
			This method toggles the visibility of the 'info' space
			It also handles the transition animation of the opening and closing
		"""
		self.show_info = not self.show_info
		if self.show_info:
			height = self.root.height * .3
		else:
			height = 0
		Animation(height=height, d=.3, t='out_quart').start(self.infoScrollView)
		self.topActionBar.infoButton.state = 'normal'

	def reset_ui(self):
		"""
			reset the UI to it's original state
			this is called when the home screen is selected
		"""
		self.topActionBar.actionSpinner.values = [self.get_string('Private_Key_Screen'), self.get_string('Vanity_Screen'), self.get_string('Mnemonic_Seed_Screen'), self.get_string('Public_Key_Screen')]
		self.privateKeyScreen.reset_ui(None)
		self.mnemonicSeedScreen.reset_ui(None)
		self.publicKeyScreen.reset_ui(None)
		self.vanityScreen.reset_ui(None)
		self.resultsScreen.reset_ui(None)
		self.linksScreenWoodWallets.reset_ui(None)
		return

	def show_popup(self, title, text):
		"""
			display a modal popup.
			used for error display
		"""
		content = BoxLayout(orientation='vertical')
		content.add_widget(Label(text=text, size_hint=(1,.7)))
		button = Button(text=self.get_string('OK'), size_hint=(1,.3))
		content.add_widget(button)
		self.popup = Popup(title=title, content=content, auto_dismiss=False, size_hint=(None, None), size=(500, 200))
		button.bind(on_press=self.close_popup)
		self.popup.open()
		self.isPopup = True
		return

	def close_popup(self, instance=False, value=False):
		"""
			Close the warning popup
		"""
		self.popup.dismiss()
		self.isPopup = False
		return

	def get_string(self, text):
		"""
			return the value for the provided string from the language json file
		"""
		try:
			return_string = self.lang[text]
		except (ValueError, KeyError):
			return_string = 'Language Error'
		return return_string

	def open_settings(*args):
		"""
			override to disable F1 settings panel
		"""
		pass


if __name__ == '__main__':
	BippyApp = BippyApp()
	BippyApp.run()
