#==================================================

import socket
import multiprocessing
from scapy.all import *

#============== L2ST CLASS ==============

class L2SocketTool:

	#============== L2ST ATTRIBUTES ==============

	l2stBuffer = None
	l2stLock = None
	l2stNetInterface = None

	#l2sfnshtBuffer = Shared Multiprocessing List
	#l2sfnshtLock = Multiprocessing Mutex
	#l2sfnshtNetInterface = String with the interface name
	def __init__(self, l2stBuffer, l2stLock, l2stNetInterface):

		self.l2stBuffer = l2stBuffer
		self.l2stLock = l2stLock
		self.l2stNetInterface = l2stNetInterface

	#============== L2ST METHODS ==============

	def l2stInput(self, pkt):

		self.l2stLock.acquire()
		self.l2stBuffer.append(bytes(pkt))
		self.l2stLock.release()

	def l2stStartInp(self):

		sniff(iface = self.l2stNetInterface, prn = self.l2stInput, store = 0, count = 0)

	def l2stStartOut(self):

		outSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
		outSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
		outSocket.bind((self.l2stNetInterface, 0))

		while True:
			if self.l2stBuffer:
				self.l2stLock.acquire()
				pkt = self.l2stBuffer.pop(0)
				self.l2stLock.release()
				outSocket.send(pkt)

#============== L2ST TEST ==============

# testManager = multiprocessing.Manager()
# l2stBuffer = testManager.list()
# l2stLock = multiprocessing.Lock()

# L2Tool = L2SocketTool(l2stBuffer, l2stLock, "eth0")

# processIn = multiprocessing.Process(target=L2Tool.l2stStartInp, args=())
# processOut = multiprocessing.Process(target=L2Tool.l2stStartOut, args=())
# processIn.start()
# processOut.start()

# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end1':
# 		processIn.terminate()
# 	if userInput == 'end2':
# 		processOut.terminate()
# 		break
# 	if userInput == 'print':
# 		print (l2stBuffer)

#==================================================