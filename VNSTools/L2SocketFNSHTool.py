#==================================================

import socket
import multiprocessing
from scapy.all import *

#============== L2SFNSHT CLASS ==============

class L2SocketFNSHTool:

	#============== L2SFNSHT ATTRIBUTES ==============

	l2sfnshtBuffer = None
	l2sfnshtLock = None
	l2sfnshtNetInterface = None
	l2sfnshtFakeNSH = None

	#l2sfnshtBuffer = Shared Multiprocessing List
	#l2sfnshtLock = Multiprocessing Mutex
	#l2sfnshtNetInterface = String with the interface name
	def __init__(self, l2sfnshtBuffer, l2sfnshtLock, l2sfnshtNetInterface):

		self.l2sfnshtBuffer = l2sfnshtBuffer
		self.l2sfnshtLock = l2sfnshtLock
		self.l2sfnshtNetInterface = l2sfnshtNetInterface
		self.l2sfnshtFakeNSH = bytearray(bytes([x for x in range(1,25)]))

	#============== L2SFNSHT METHODS ==============

	def l2sfnshtInput(self, pkt):

		if len(bytes(pkt)) <= 1450: #Fragmentação Ethernet - Resolver em algum momento
			pkt = bytearray(bytes(pkt))
			pkt = pkt[0:14] + self.l2sfnshtFakeNSH + pkt[14:]
			self.l2sfnshtLock.acquire()
			self.l2sfnshtBuffer.append(bytes(pkt))
			self.l2sfnshtLock.release()

	def l2sfnshtStartInp(self):

		sniff(iface = self.l2sfnshtNetInterface, filter = "eth", prn = self.l2sfnshtInput, store = 0, count = 0)

	def l2sfnshtStartOut(self):

		outSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
		outSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
		outSocket.bind((self.l2sfnshtNetInterface, 0))

		while True:
			if self.l2sfnshtBuffer:
				self.l2sfnshtLock.acquire()
				pkt = self.l2sfnshtBuffer.pop(0)
				self.l2sfnshtLock.release()
				outSocket.send(pkt)

#============== L2SFNSHT TEST ==============

# testManager = multiprocessing.Manager()
# l2sfnshtBuffer = testManager.list()
# l2sfnshtLock = multiprocessing.Lock()

# L2Tool = L2SocketFNSHTool(l2sfnshtBuffer, l2sfnshtLock, "eth0")

# processIn = multiprocessing.Process(target=L2Tool.l2sfnshtStartInp, args=())
# processOut = multiprocessing.Process(target=L2Tool.l2sfnshtStartOut, args=())
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
# 		print (l2sfnshtBuffer)

#==================================================