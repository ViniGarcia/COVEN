#==================================================

import subprocess
import os

#============== EXE CLASS ==============

class ExeFramework:

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

		os.system("chmod +x " + self.exefNFPath)

		if not self.exefNFPath.startswith('/') and not self.exefNFPath.startswith('./'):
			self.exefNFPath = './' + self.exefNFPath

		if self.exefNFArgs:
			self.exefNFProcess = subprocess.Popen([self.exefNFPath] + self.exefNFArgs)
		else:
			self.exefNFProcess = subprocess.Popen([self.exefNFPath])

	def stop(self):

		self.exefNFProcess.terminate()

#============== EXE TEST ==============

# ExecutableFramework = ExeFramework('ForwardC', None)
# ExecutableFramework.start()
#
# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		ExecutableFramework.stop()
# 		break

#==================================================
