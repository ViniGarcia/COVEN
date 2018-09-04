#==================================================

import multiprocessing
from scapy.all import *
from sys import path
path.insert(0, 'VNSTools/')
from L2SocketTool import L2SocketTool
from L2SocketFNSHTool import L2SocketFNSHTool

#============== VNS SUBCLASS ==============

class VNSInstance:

	vnsiTool = None
	vnsiProcess = None

	def __init__(self, vnsiTool, vnsiProcess):

		self.vnsiTool = vnsiTool
		self.vnsiProcess = vnsiProcess

	def vnsiStart(self):
		self.vnsiProcess.start()

	def vnsiStop(self):
		self.vnsiProcess.terminate()

#============== VNS CLASS ==============

class VNetSubsystem:

	#============== VNS ATTRIBUTES ==============

	vnsManager = None
	vnsTool = None
	vnsInBuffers = None
	vnsInInstances = None
	vnsOutBuffers = None
	vnsOutInstances = None

	#vnsTool = String with the chosen tool
	#vnsInIfaces = List of Strings with input interfaces names
	#vnsOutIfaces = List of Strings with output interfaces names
	def __init__(self, vnsTool, vnsInIfaces, vnsOutIfaces):

		self.vnsManager = multiprocessing.Manager()
		self.vnsTool = vnsTool

		self.vnsInBuffers = {}
		for iface in vnsInIfaces:
			self.vnsInBuffers[iface] = (self.vnsManager.list(), multiprocessing.Lock())

		self.vnsOutBuffers = {}
		for iface in vnsOutIfaces:
			self.vnsOutBuffers[iface] = (self.vnsManager.list(), multiprocessing.Lock())

		self.vnsInInstances = {}
		self.vnsOutInstances = {}
		if self.vnsTool == 'L2Socket':
			for iface in self.vnsInBuffers:
				vnsiTool = L2SocketTool(self.vnsInBuffers[iface][0], self.vnsInBuffers[iface][1], iface)
				vnsiProcess = multiprocessing.Process(target=vnsiTool.l2stStartInp, args=())
				self.vnsInInstances[iface] = VNSInstance(vnsiTool, vnsiProcess)

			for iface in self.vnsOutBuffers:
				vnsiTool = L2SocketTool(self.vnsOutBuffers[iface][0], self.vnsOutBuffers[iface][1], iface)
				vnsiProcess = multiprocessing.Process(target=vnsiTool.l2stStartOut, args=())
				self.vnsOutInstances[iface] = VNSInstance(vnsiTool, vnsiProcess)

			return

		if self.vnsTool == 'L2SocketFNSH':
			for iface in self.vnsInBuffers:
				vnsiTool = L2SocketFNSHTool(self.vnsInBuffers[iface][0], self.vnsInBuffers[iface][1], iface)
				vnsiProcess = multiprocessing.Process(target=vnsiTool.l2sfnshtStartInp, args=())
				self.vnsInInstances[iface] = VNSInstance(vnsiTool, vnsiProcess)

			for iface in self.vnsOutBuffers:
				vnsiTool = L2SocketFNSHTool(self.vnsOutBuffers[iface][0], self.vnsOutBuffers[iface][1], iface)
				vnsiProcess = multiprocessing.Process(target=vnsiTool.l2sfnshtStartOut, args=())
				self.vnsOutInstances[iface] = VNSInstance(vnsiTool, vnsiProcess)

			return

	#============== VNS METHODS ==============

	def vnsStart(self):
		
		for iface in self.vnsInInstances:
			self.vnsInInstances[iface].vnsiStart()
		for iface in self.vnsOutInstances:
			self.vnsOutInstances[iface].vnsiStart()

	def vnsStop(self):
		for iface in self.vnsInInstances:
			self.vnsInInstances[iface].vnsiStop()
		for iface in self.vnsOutInstances:
			self.vnsOutInstances[iface].vnsiStop()


#============== VNS TEST ==============

# VNSubsys = VNetSubsystem('L2Socket', ['eth0', 'wlan0'], ['wlan0'])
# VNSubsys.vnsStart()

# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		VNSubsys.vnsStop()
# 		break
# 	if userInput == 'eth0':
# 		print (VNSubsys.vnsInInstances['eth0'].vnsiTool.l2stBuffer)
# 	if userInput == 'wlan0':
# 		print (VNSubsys.vnsInInstances['wlan0'].vnsiTool.l2stBuffer)

#==================================================



			

		

