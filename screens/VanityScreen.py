from kivy.uix.screenmanager import Screen
import subprocess
import atexit
import os
from kivy.clock import Clock
import system.gen as gen
from platform import system, architecture

class VanityScreen(Screen):
	"""
		Display the actions that work with vanity addresses
	"""

	def __init__(self, BippyApp, **kwargs):
		super(VanityScreen, self).__init__(**kwargs)

		self.BippyApp = BippyApp
		self.vanity = ''
		self.timer = None
		self.address = ''
		self.privkey = ''
		self.passphrase = ''
		self.command = []

		self.mainLayout = self.ids.mainLayout.__self__
		self.mainLabel = self.ids.mainLabel.__self__
		self.vanityLabel = self.ids.vanityLabel.__self__
		self.vanityInput = self.ids.vanityInput.__self__
		self.submitButton = self.ids.submitButton.__self__

		self.abortButton = self.ids.abortButton.__self__

		self.yesButtonInfo = self.ids.yesButtonInfo.__self__
		self.noButtonInfo = self.ids.noButtonInfo.__self__
		self.yesButtonEncrypt = self.ids.yesButtonEncrypt.__self__
		self.noButtonEncrypt = self.ids.noButtonEncrypt.__self__

		self.passfieldLabel = self.ids.passfieldLabel.__self__
		self.passfield = self.ids.passfield.__self__
		self.feedback = self.ids.feedback.__self__
		self.checkfieldLabel = self.ids.checkfieldLabel.__self__
		self.checkfield = self.ids.checkfield.__self__

		self.reset_ui(None)
		return

	def reset_ui(self, dt):
		#set up for first use
		self.mainLayout.clear_widgets()
		self.mainLabel.text = self.BippyApp.get_string('Vanity_Intro_Text')
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.vanityLabel)
		self.vanityInput.text = ''
		self.mainLayout.add_widget(self.vanityInput)
		self.mainLayout.add_widget(self.submitButton)

		self.passfield.text =''
		self.checkfield.text = ''
		self.passphrase = ''

		self.vanity = ''
		self.timer = None
		self.address = ''
		self.privkey = ''
		return

	def submit_vanity(self, vanity, command=''):
		"""
			submit the vanity text and pass it to vanitygen_linux_64 for a test run

			we simulate a full run. This will give us the difficulty and the first three system info outputs
			if the vanity is very easy we may get the address and private key in the output of the simulation
			otherwise we can show an estimation of how long generation will take to the user
		"""
		if not self.BippyApp.check_chosen_currency():
			return
		#store the vanity text for later use
		self.vanity = vanity
		#build the command
		if command == '':
			#vanitygen linux
			if system() == 'Linux':
				if architecture()[0] == '64bit':
					self.command = ['./res/vanitygen/vanitygen_linux_64']
				else:
					self.command = ['./res/vanitygen/vanitygen_linux']
			#Windows
			if system() == 'Windows':
				if architecture()[0] == '64bit':
					self.command = ['./res/vanitygen/vanitygen_win_64']
				else:
					self.command = ['./res/vanitygen/vanitygen_win']
			#Mac
			if system() == 'Darwin':
				if architecture()[0] == '64bit':
					self.command = ['./res/vanitygen/vanitygen_mac_64']
				else:
					self.command = ['./res/vanitygen/vanitygen_mac']
			
			for cur in self.BippyApp.currencies:
				if cur['currency'] == self.BippyApp.chosenCurrency:
					self.command.append('-X ' + str(cur['version']))
					self.command.append('-n')
					self.command.append(cur['prefix'] + str(self.vanity))

		output = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		#first check for errors
		error = output.stderr.read()
		if error != '':
			#there's a few things to try, we can turn on case insensitivity (-i) and try the match as a regex too (-r).
			#try each in turn
			if '-i' not in self.command:
				self.command.append('-i')
				self.submit_vanity(self.vanity, self.command)
				self.BippyApp.show_popup(self.BippyApp.get_string('Warning'), self.BippyApp.get_string('Case_Sensitivity_Warning'))
				return
			if '-r' not in self.command:
				self.command.append('-r')
				self.submit_vanity(self.vanity, self.command)
				self.BippyApp.show_popup(self.BippyApp.get_string('Warning'), self.BippyApp.get_string('Regex_Warning'))
				return
			#if we get here, none of the above worked so show the error
			self.BippyApp.show_popup(self.BippyApp.get_string('Popup_Error'), error)
			return
		#now see if an easy vanity pattern was found during the simulation
		values = output.stdout.read()
		if 'Pattern:' in values:
			self.display_vanity(values)
		else:
			#we have a stdout file object that contains difficulty and three rows of system info.
			#we display that to the user to allow them to decide if they want to undertake the generation
			self.display_system_info(values)
		return

	def get_system_info(self, data1, data2):
		"""
			calculate the system information and estimated time to address based on the two lines of good data
			we can return rate, a time estimate with percentage change attached
			units:
				rate -> keys/second
				time -> seconds
				percentage -> percent
		"""
		rate = int((int(data1.split('|')[0]) + int(data2.split('|')[0])) / 2)
		percentage = int((int(data1.split('|')[1]) + int(data2.split('|')[1])) / 2)
		time = int((int(data1.split('|')[2]) + int(data2.split('|')[2])) / 2)
		return rate, time, percentage

	def display_system_info(self, values):
		"""
			show the system information from the vanitygen_linux_64 simulation process to the user
		"""
		val = values.split('\n')
		#first row is difficulty
		difficulty = val[0].split(':')[1].strip()
		#next three lines are system info
		#we are only really interested in the last two though as the first never seems to give the correct estimates
		#send that necessary data to the function for parsing
		rate, time, percentage = self.get_system_info(val[2], val[3])

		#unit conversion of rate and time
		rate_unit = 'keys/sec'
		if rate > 1000:
			rate = (rate / 1000)
			rate_unit = 'Kkeys/sec'
		if rate > 1000:
			rate = (rate / 1000)
			rate_unit = 'Mkeys/sec'

		time_unit = 'seconds'
		if time > 60:
			time = (time / 60)
			time_unit = 'minutes'
		if time > 60:
			time = (time / 60)
			time_unit = 'hours'
		if time > 24:
			time = (time / 24)
			time_unit = 'days'
		if time > 365:
			time = (time / 365)
			time_unit = 'years'

		output = self.BippyApp.get_string('System_Info_1') + self.BippyApp.chosenCurrency + self.BippyApp.get_string('System_Info_2') + self.vanity \
		         + self.BippyApp.get_string('System_Info_3') + difficulty + self.BippyApp.get_string('System_Info_4') \
		         + self.BippyApp.get_string('System_Info_5') + str(rate) + ' ' + rate_unit + '.' \
		         + self.BippyApp.get_string('System_Info_6') + str(percentage) + self.BippyApp.get_string('System_Info_7') \
		         + str(time) + ' ' + time_unit + self.BippyApp.get_string('System_Info_8')
		self.mainLayout.clear_widgets()
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLabel.text = output
		self.mainLayout.add_widget(self.yesButtonInfo)
		self.mainLayout.add_widget(self.noButtonInfo)
		return

	def show_password(self):
		"""
			set up the ui ready for password entry
		"""
		self.mainLayout.clear_widgets()
		self.mainLabel.text = self.BippyApp.get_string('Vanity_Passphrase')
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.passfieldLabel)
		self.mainLayout.add_widget(self.passfield)
		self.mainLayout.add_widget(self.feedback)
		self.mainLayout.add_widget(self.checkfieldLabel)
		self.mainLayout.add_widget(self.checkfield)
		self.passfield.focus = True
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
			passfield.text = passphrase.replace('\t', '')
			checkfield.focus = True
			return
		if '\t' in checktext:
			checkfield.text = checktext.replace('\t', '')
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
			button.text = self.BippyApp.get_string('Encrypt')
			layout.add_widget(button)
			self.passphrase = passphrase
			return

	def update_counter(self, dt):
		"""
			Update the timer on the mainLabel
		"""
		self.timer = 1 if self.timer is None else (self.timer + 1)
		minutes = (self.timer / 60)
		hours = (minutes / 60)
		days = (hours / 24)
		years = (days / 365)
		seconds = self.timer % 60
		counter = (str(years).zfill(2) + ' years ') \
                  + (str(days).zfill(2) + ' days ') \
                  + (str(hours).zfill(2) + ' hours ') \
                  + (str(minutes).zfill(2) + ' minutes ') \
                  + str(seconds).zfill(2) + ' seconds'
		self.mainLayout.clear_widgets()
		self.mainLabel.text = self.BippyApp.get_string('Starting_Search') + '\n\n\n' \
		                      + self.BippyApp.get_string('Approximate_Time') + '\n' + counter
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.abortButton)
		return

	def read_output(self, dt):
		"""
			read the output of the vanitygen_linux_64 program and see if an address has been found
		"""
		line = self.output.stdout.readline()
		if 'Address:' in line:
			Clock.unschedule(self.update_counter)
			Clock.unschedule(self.read_output)
			line += self.output.stdout.readline()
			self.display_vanity(line)
		return

	def abort_vanitygen(self):
		"""
		    kill the vanitygen_linux_64 search and reset the ui
		"""
		Clock.unschedule(self.update_counter)
		Clock.unschedule(self.read_output)
		os.kill(self.output.pid, 9)
		self.reset_ui(None)
		return

	def run_vanitygen(self):
		"""
			run the vanitygen_linux_64 executable without the 'simulate' flag
		"""
		self.counter = Clock.schedule_interval(self.update_counter, 1)
		self.reader = Clock.schedule_interval(self.read_output, 0.1)
		#self.command contains the full command we tested with so should work first time
		self.command.remove('-n')
		self.output = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		def kill_vanitygen():
			"""
				kill the vanitygen_linux_64 process.
				designed to be called atexit to cancel any unwanted long-running process
			"""
			os.kill(self.output.pid, 9)
			return

		atexit.register(kill_vanitygen)
		return

	def display_vanity(self, values):
		"""
			show the results of the vanitygen_linux_64 process to the user
		"""
		lines = values.split('\n')
		for line in lines:
			if 'Address:' in line:
				self.address = line.split(':')[1].strip()
			if 'Privkey:' in line:
				self.privkey = line.split(':')[1].strip()
		self.mainLayout.clear_widgets()
		self.mainLayout.add_widget(self.mainLabel)
		self.mainLayout.add_widget(self.yesButtonEncrypt)
		self.mainLayout.add_widget(self.noButtonEncrypt)
		self.mainLabel.text = self.BippyApp.get_string('Display_Vanity_1') + self.address \
		                    + self.BippyApp.get_string('Display_Vanity_2')
		return

	def display_result(self):
		"""
			set up the results page and pass the variables to them
		"""
		resultsScreen = self.BippyApp.mainScreenManager.get_screen('Results')
		resultsScreen.display_wif_vanity(self.privkey, self.address)

	def encrypt_privkey(self):
		"""
			BIP0038 encrypt the generated private key
		"""
		self.mainLayout.clear_widgets()
		self.mainLabel.text = self.BippyApp.get_string('Starting_Bip')
		self.mainLayout.add_widget(self.mainLabel)
		Clock.schedule_once(self.encrypt, 0.5)

	def encrypt(self, dt):
		"""
			Perform the actual encryption
		"""
		BIP, Address = gen.encBIPKey(self.privkey, self.BippyApp.chosenCurrency, self.passphrase)
		resultsScreen = self.BippyApp.mainScreenManager.get_screen('Results')
		resultsScreen.display_bip(BIP, Address)

		#clear the UI
		Clock.schedule_once(self.reset_ui, 5)
