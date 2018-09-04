#==================================================

from sys import path
path.insert(0, 'PPSFrameworks/')
from Python3Framework import Python3Framework
from ClickFramework import ClickFramework

#============== PPS CLASS ==============

class PProcSubsystem:

	#============== PPS ATTRIBUTES ==============

	ppsfInstances = None

	#ppsVNFConf = List of Triples, the Triples has:
	#			  [0] String indicating the chosen framework
	#			  [1] String indicating the NF file path
	#			  [2] List of Strings with the NF arguments
	def __init__(self, ppsNFConf):

		self.ppsfInstances = []
		
		for NF in ppsNFConf:	
			if NF[0] == 'Python3Framework':
				self.ppsfInstances.append(Python3Framework(NF[1], NF[2]))
				continue
			if NF[0] == 'ClickFramework':
				self.ppsfInstances.append(ClickFramework(NF[1], NF[2]))
				continue

			self.ppsfInstances = None
			return

	#============== PPS METHODS ==============

	def ppsStart(self):

		for instance in self.ppsfInstances:
			instance.start()

	def ppsStop(self):

		for instance in self.ppsfInstances:
			instance.stop()

#============== PPS TEST ==============

# PPSInstance = PProcSubsystem([('Python3Framework','Forward1.py', None), ('Python3Framework','Forward2.py', None)])

# PPSInstance.ppsStart()
# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		PPSInstance.ppsStop()
# 		break

#==================================================