#==================================================

import subprocess
import os

#============== P3F CLASS ==============

class Python3Framework:

	#============== P3F ATTRIBUTES ==============

	p3fNFPath = None
	p3fNFArgs = None
	p3fNFProcess = None

	#p3fNFPath = String with NF file path
	#p3fNFArgs = List of Strings with each NF argument
	def __init__(self, p3fNFPath, p3fNFArgs):

		if not os.path.isfile(p3fNFPath):
			return

		self.p3fNFPath = p3fNFPath
		self.p3fNFArgs = p3fNFArgs

	#============== P3F METHODS ==============

	def start(self):

		if self.p3fNFArgs:
			self.p3fNFProcess = subprocess.Popen(['python3', self.p3fNFPath] + self.p3fNFArgs)
		else:
			self.p3fNFProcess = subprocess.Popen(['python3', self.p3fNFPath])

	def stop(self):

		self.p3fNFProcess.terminate()

#============== P3F TEST ==============

# P3Framework = Python3Framework('Forward1.py', None)
# P3Framework.start()

# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		P3Framework.stop()
# 		break

#==================================================