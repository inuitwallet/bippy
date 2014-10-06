from kivy.uix.screenmanager import Screen

class IntermediateCodeScreen(Screen):
	"""
		The Intermediate Code Generation Screen
	"""

	def __init__(self, BippyApp, **kwargs):
		super(IntermediateCodeScreen, self).__init__(**kwargs)
		self.BippyApp = BippyApp
		return
