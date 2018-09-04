#==================================================

import subprocess
import os

#============== CF CLASS ==============

class ClickFramework:

	#============== CF ATTRIBUTES ==============

	cfNFPath = None
	cfNFArgs = None
	cfNFProcess = None

	#cfNFPath = String with NF file path
	#cfNFArgs = List of Strings with each NF argument
	def __init__(self, cfNFPath, cfNFArgs):

		if not os.path.isfile(cfNFPath):
			return

		self.cfNFPath = cfNFPath
		self.cfNFArgs = cfNFArgs

	#============== CF METHODS ==============

	def start(self):

		if self.cfNFArgs:
			self.cfNFProcess = subprocess.Popen(['click', '-f', self.cfNFPath] + self.cfNFArgs)
		else:
			self.cfNFProcess = subprocess.Popen(['click', '-f', self.cfNFPath])

	def stop(self):

		self.cfNFProcess.terminate()

#============== CF TEST ==============

# CFramework = Python3Framework('Forward1.py', None)
# CFramework.start()

# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		CFramework.stop()
# 		break

#==================================================