#==================================================

import subprocess
import os

#============== JSF CLASS ==============

class JSFramework:

	#============== JSF ATTRIBUTES ==============

	jsfNFPath = None
	jsfNFArgs = None
	jsfNFProcess = None

	#jsfNFPath = String with NF file path
	#jsfNFArgs = List of Strings with each NF argument
	def __init__(self, jsfNFPath, jsfNFArgs):

		if not os.path.isfile(jsfNFPath):
			return

		self.jsfNFPath = jsfNFPath
		self.jsfNFArgs = jsfNFArgs

	#============== JSF METHODS ==============

	def start(self):

		if self.jsfNFArgs:
			self.jsfNFProcess = subprocess.Popen(['nodejs', self.jsfNFPath] + self.jsfNFArgs)
		else:
			self.jsfNFProcess = subprocess.Popen(['nodejs', self.jsfNFPath])

	def stop(self):

		self.jsfNFProcess.terminate()

#============== JSF TEST ==============

# JavaScriptFramework = JSFramework('Forward.js', None)
# JavaScriptFramework.start()
#
# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		JavaScriptFramework.stop()
# 		break

#==================================================
