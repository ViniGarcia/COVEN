#==================================================

import subprocess
import os

#============== EXE CLASS ==============

class EXEFramework:

	#============== EXE ATTRIBUTES ==============

	exefNFPath = None
	exefNFArgs = None
	exefNFProcess = None

	#exefNFPath = String with NF file path
	#exefNFArgs = List of Strings with each NF argument
	def __init__(self, exefNFPath, exefNFArgs):

		if not os.path.isfile(exefNFPath):
			return

		self.exefNFPath = exefNFPath
		self.exefNFArgs = exefNFArgs

	#============== EXE METHODS ==============

	def start(self):

		if self.exefNFArgs:
			self.exefNFProcess = subprocess.Popen(['./' + self.exefNFPath] + self.exefNFArgs)
		else:
			self.exefNFProcess = subprocess.Popen(['./' + self.exefNFPath])

	def stop(self):

		self.exefNFProcess.terminate()

#============== EXE TEST ==============

# ExecutableFramework = EXEFramework('ForwardC', None)
# ExecutableFramework.start()
#
# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		ExecutableFramework.stop()
# 		break

#==================================================
