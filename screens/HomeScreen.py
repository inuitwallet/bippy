from kivy.uix.screenmanager import Screen

class HomeScreen(Screen):
	"""
		The Welcome Screen
	"""

	def __init__(self, BippyApp, **kwargs):
		super(HomeScreen, self).__init__(**kwargs)
		self.BippyApp = BippyApp
		return
