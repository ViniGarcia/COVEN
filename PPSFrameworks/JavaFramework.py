#==================================================

import subprocess
import os

#============== JAVA CLASS ==============

class JavaFramework:

	#============== JAVA ATTRIBUTES ==============

	javafNFFile = None
	javafNFPath = None
	javafNFArgs = None
	javafNFProcess = None

	#javafNFPath = String with NF file path
	#javafNFArgs = List of Strings with each NF argument
	def __init__(self, javafNFPath, javafNFArgs):

		if not os.path.isfile(javafNFPath):
			return
		if (len(javafNFPath) > 5) and (not os.path.isfile(javafNFPath[0:len(javafNFPath)-5] + '.class')):
			return

		self.javafNFFile = javafNFPath[javafNFPath.rfind('/')+1:len(javafNFPath)-5]
		self.javafNFPath = javafNFPath[0:javafNFPath.rfind('/')+1]
		self.javafNFArgs = javafNFArgs

	#============== JAVA METHODS ==============

	def start(self):

		if self.javafNFArgs:
			self.javafNFProcess = subprocess.Popen(['java', '-classpath', self.javafNFPath, self.javafNFFile] + self.javafNFArgs)
		else:
			self.javafNFProcess = subprocess.Popen(['java', '-classpath', self.javafNFPath, self.javafNFFile])

	def stop(self):

		self.javafNFProcess.terminate()

#============== JAVA TEST ==============

# JFramework = JavaFramework('../Example/Forward.java', None)
# JFramework.start()
#
# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		JFramework.stop()
# 		break

#==================================================
