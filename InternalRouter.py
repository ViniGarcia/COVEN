#==================================================

import multiprocessing
import socket
from scapy.all import *

from PProcSubsystem import PProcSubsystem
from VNetSubsystem import VNetSubsystem
from NSHProcessor import NSHProcessor

#============== IR SUBCLASS ==============

class ppsiCommunication:

	ppsiInPort = None
	ppsiOutPort = None
	ppsiInSocket = None
	ppsiOutSocket = None

	ppsiInConn = None

	def __init__(self, ppsiInPort, ppsiOutPort):

		self.ppsiInPort = ppsiInPort
		self.ppsiOutPort = ppsiOutPort
		if self.ppsiInPort:
			self.ppsiInSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.ppsiInSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
		if self.ppsiOutPort:
			self.ppsiOutSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.ppsiOutSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)

	def ppsiStart(self):

		self.ppsiInSocket.bind(('localhost', self.ppsiInPort))
		self.ppsiInSocket.listen(1)
		self.ppsiInConn, clientData = self.ppsiInSocket.accept()
		self.ppsiOutSocket.connect(('localhost', self.ppsiOutPort))

		while (True):
			pkt = self.ppsiInConn.recv(1514)
			self.ppsiOutSocket.send(pkt)

#============== IR CLASS ==============

class InternalRouter:

	#============== IR ATTRIBUTES ==============

	irOrdIntPorts = None

	irInputConnection = None
	irRemNSHPConnection = None
	irInternalConnections = None
	irReiNSHPConnection = None
	irOutputConnection = None

	irIngressSocket = None
	irEgressSocket = None
	irEgressConnection = None

	PPSPPSProcesses = None
	VNSPPSProcess = None
	VNSNSHPProcess = None
	NSHPPPSProcess = None
	PPSVNSProcess = None
	PPSNSHPProcess = None
	NSHPVNSProcess = None

	def __init__(self, vnsInstance, nshpInstance, irOrdIntPorts):

		if vnsInstance.vnsInBuffers:
			self.irInputConnection = vnsInstance.vnsInBuffers[list(vnsInstance.vnsInBuffers.keys())[0]]
		if vnsInstance.vnsOutBuffers:
			self.irOutputConnection = vnsInstance.vnsOutBuffers[list(vnsInstance.vnsOutBuffers.keys())[0]]
		if nshpInstance:
			self.irRemNSHPConnection = [(nshpInstance.remInputArray, nshpInstance.remInSharedLock), (nshpInstance.remOutputArray, nshpInstance.remOutSharedLock)]
			self.irReiNSHPConnection = [(nshpInstance.reiInputArray, nshpInstance.reiInSharedLock), (nshpInstance.reiOutputArray, nshpInstance.reiOutSharedLock)]
		if irOrdIntPorts:
			self.irOrdIntPorts = irOrdIntPorts
			self.irIngressSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.irIngressSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
			self.irEgressSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.irIngressSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)

	#============== IR METHODS ==============

	def irPPSPPSServer(self):

		if self.irOrdIntPorts:
			self.irInternalConnections = []
			for index in range(len(self.irOrdIntPorts)-1):
				self.irInternalConnections.append(ppsiCommunication(self.irOrdIntPorts[index][1], self.irOrdIntPorts[index+1][0]))

	def irVNSPPSServer(self):

		if self.irOrdIntPorts:
			self.irIngressSocket.connect(('localhost', self.irOrdIntPorts[0][0]))
		else:
			return

		while True:
			if self.irInputConnection[0]:
				self.irInputConnection[1].acquire()
				pkt = self.irInputConnection[0].pop(0)
				self.irInputConnection[1].release()
				self.irIngressSocket.send(pkt)

	def irVNSNSHPServer(self):

		if not self.irOrdIntPorts:
			return

		while True:
			if self.irInputConnection[0]:
				self.irInputConnection[1].acquire()
				pkt = self.irInputConnection[0].pop(0)
				self.irInputConnection[1].release()
				self.irRemNSHPConnection[0][1].acquire()
				self.irRemNSHPConnection[0][0].append(pkt)
				self.irRemNSHPConnection[0][1].release()

	def irNSHPPPSServer(self):

		if self.irOrdIntPorts:
			self.irIngressSocket.connect(('localhost', self.irOrdIntPorts[0][0]))
		else:
			return

		while True:
			if self.irRemNSHPConnection[1][0]:
				self.irRemNSHPConnection[1][1].acquire()
				pkt = self.irRemNSHPConnection[1][0].pop(0)
				self.irRemNSHPConnection[1][1].release()
				self.irIngressSocket.send(pkt)

	def irPPSNSHPServer(self):

		if self.irOrdIntPorts:
			self.irEgressSocket.bind(('localhost', self.irOrdIntPorts[-1][1]))
			self.irEgressSocket.listen(1)
			self.irEgressConnection, clientData = self.irEgressSocket.accept()
		else:
			return

		while True:
			pkt = self.irEgressConnection.recv(1514)
			self.irReiNSHPConnection[0][1].acquire()
			self.irReiNSHPConnection[0][0].append(pkt)
			self.irReiNSHPConnection[0][1].release()

	def irNSHPVNSServer(self):

		if not self.irOrdIntPorts:
			return

		while True:
			if self.irReiNSHPConnection[1][0]:
				self.irReiNSHPConnection[1][1].acquire()
				pkt = self.irReiNSHPConnection[1][0].pop(0)
				self.irReiNSHPConnection[1][1].release()
				self.irOutputConnection[1].acquire()
				self.irOutputConnection[0].append(pkt)
				self.irOutputConnection[1].release()

	def irPPSVNSServer(self):

		if self.irOrdIntPorts:
			self.irEgressSocket.bind(('localhost', self.irOrdIntPorts[-1][1]))
			self.irEgressSocket.listen(1)
			self.irEgressConnection, clientData = self.irEgressSocket.accept()
		else:
			return

		while True:
			pkt = self.irEgressConnection.recv(1514)
			self.irOutputConnection[1].acquire()
			self.irOutputConnection[0].append(pkt)
			self.irOutputConnection[1].release()

	def irNetworkStart(self):

		if self.irRemNSHPConnection != None:
			self.PPSNSHPProcess = multiprocessing.Process(target=self.irPPSNSHPServer, args=())
			self.PPSNSHPProcess.start()
		else:
			self.PPSVNSProcess = multiprocessing.Process(target=self.irPPSVNSServer, args=())
			self.PPSVNSProcess.start()

		self.irPPSPPSServer()
		if self.irOrdIntPorts:
			self.PPSPPSProcesses = []
			for intComm in self.irInternalConnections:
				process = multiprocessing.Process(target=intComm.ppsiStart, args=())
				process.start()
				self.PPSPPSProcesses.append(process)

	def irModulesStart(self):

		if self.irRemNSHPConnection != None:
			self.VNSNSHPProcess = multiprocessing.Process(target=self.irVNSNSHPServer, args=())
			self.VNSNSHPProcess.start()
			self.NSHPVNSProcess = multiprocessing.Process(target=self.irNSHPVNSServer, args=())
			self.NSHPVNSProcess.start()
			self.NSHPPPSProcess = multiprocessing.Process(target=self.irNSHPPPSServer, args=())
			self.NSHPPPSProcess.start()
		else:
			self.VNSPPSProcess = multiprocessing.Process(target=self.irVNSPPSServer, args=())
			self.VNSPPSProcess.start()

	def irStop(self):

		if self.PPSPPSProcesses:
			for process in self.PPSPPSProcesses:
				process.terminate()

		if self.irRemNSHPConnection != None:
			self.VNSNSHPProcess.terminate()
			self.NSHPPPSProcess.terminate()
			self.PPSNSHPProcess.terminate()
			self.NSHPVNSProcess.terminate()
		else:
			self.VNSPPSProcess.terminate()
			self.PPSVNSProcess.terminate()


#============== IR TEST (NO NSH) ==============

# import time
# ppsInstace = PProcSubsystem([('Python3Framework','Forward1.py', None), ('Python3Framework','Forward2.py', None)])
# ppsInstace.ppsStart()
# time.sleep(0.01)
# vnsInstance = VNetSubsystem('L2Socket', ['eth0'], ['wlan0'])
# vnsInstance.vnsStart()
# time.sleep(0.01)
# # nshpInstance = NSHProcessor()
# # nshpInstance.nshpStart()
# # time.sleep(0.01)
# irInstance = InternalRouter(vnsInstance, None, [(7000,7001),(7002,7003)])
# irInstance.irStart()

# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		irInstance.irStop()
# 		vnsInstance.vnsStop()
# 		# nshpInstance.nshpStop()
# 		ppsInstace.ppsStop()
# 		break
# 	if userInput == 'rawin':
# 		print (irInstance.irInputConnection[0])
# 	if userInput == 'rawout':
# 		print (irInstance.irOutputConnection[0])

#==================================================

#============== IR TEST (WITH NSH) ==============

# import time
# ppsInstace = PProcSubsystem([('Python3Framework','Forward1.py', None), ('Python3Framework','Forward2.py', None)])
# ppsInstace.ppsStart()
# time.sleep(0.01)
# vnsInstance = VNetSubsystem('L2SocketFNSH', ['eth0'], ['wlan0'])
# vnsInstance.vnsStart()
# time.sleep(0.01)
# nshpInstance = NSHProcessor()
# nshpInstance.nshpStart()
# time.sleep(0.01)
# irInstance = InternalRouter(vnsInstance, nshpInstance, [(8010,8011),(8012,8013)])
# irInstance.irStart()

# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		irInstance.irStop()
# 		vnsInstance.vnsStop()
# 		nshpInstance.nshpStop()
#		ppsInstace.ppsStop()
# 		break
# 	if userInput == 'rawin':
# 		print (irInstance.irInputConnection[0])
# 	if userInput == 'rawout':
# 		print (irInstance.irOutputConnection[0])

#==================================================
