#==================================================

import multiprocessing
from bottle import route, run, request
from scapy.all import *

#============== NSHP CLASS ==============

class NSHProcessor:
	
	#============== NSHP ATTRIBUTES ==============

	nshpManager = None
	packetsNSHLock = None
	packetsNSH = None
	packetsIndexes = None

	remInSharedLock = None 
	remInputArray = None
	remOutSharedLock = None
	remOutputArray = None

	reiInSharedLock = None 
	reiInputArray = None
	reiOutSharedLock = None
	reiOutputArray = None

	processRem = None
	processRei = None
	processUpd = None

	def __init__(self):

		self.nshpManager = multiprocessing.Manager()
		self.packetsNSHLock = multiprocessing.Lock()
		self.packetsNSH = self.nshpManager.dict()
		self.packetsIndexes = 0

		self.remInSharedLock = multiprocessing.Lock()
		self.remInputArray = self.nshpManager.list()
		self.remOutSharedLock = multiprocessing.Lock()
		self.remOutputArray = self.nshpManager.list()

		self.reiInSharedLock = multiprocessing.Lock()
		self.reiInputArray = self.nshpManager.list()
		self.reiOutSharedLock = multiprocessing.Lock()
		self.reiOutputArray = self.nshpManager.list()

	#============== NSHP METHODS ==============

	def nshpRemoval(self, pkt):

		#Packet serialization
		packetBytes = bytearray(bytes(pkt))
		nshHeader = packetBytes[14:38]
		strippedPacket = packetBytes[0:14] + packetBytes[38:]

		#Packet Registration
		if self.packetsIndexes == 2147483641:
			self.packetsIndexes = 0
		self.packetsNSHLock.acquire()
		self.packetsNSH[self.packetsIndexes] = nshHeader
		self.packetsNSHLock.release()
		bytesIndex = self.packetsIndexes.to_bytes(4, byteorder='big')
		strippedPacket += bytesIndex
		self.packetsIndexes += 1

		return bytes(strippedPacket)

	def nshpReinsert(self, pkt):

		#Packet serialization
		packetBytes = bytearray(pkt)

		#NSH recovering
		packetIndex = int(packetBytes[-4]) << 24 | int(packetBytes[-3]) << 16 | int(packetBytes[-2]) << 8 | int(packetBytes[-1])
		self.packetsNSHLock.acquire()
		nshHeader = self.packetsNSH[packetIndex]
		del self.packetsNSH[packetIndex]
		self.packetsNSHLock.release()

		#Packet internal index removing
		packetBytes = packetBytes[:-4]

		#SI drecementation
		SI = nshHeader[14] << 8 | nshHeader[15]
		SI = (SI-1).to_bytes(2, byteorder='big')
		nshHeader[14] = SI[0]
		nshHeader[15] = SI[1]

		#NSH reallocation
		packetBytes = packetBytes[0:14] + nshHeader + packetBytes[14:]

		return bytes(packetBytes)

	@route('/nshp/updateci', method='POST')
	def nshpUpdateCI(self):

		nshData = literal_eval(request.body.read())
		if len(nshData) != 2:
			return '-1'
		if len(nshData[0]) < 4:
			return '-2'

		nshIndex = int(nshData[0][-4]) << 24 | int(nshData[0][-3]) << 16 | int(nshData[0][-2]) << 8 | int(nshData[0][-1])
		if not nshIndex in self.packetsNSH:
			return '-3'
		if len(nshData[1]) != 16:
			return '-4'

		nshCI = bytes(nshData[1])
		nshHeader = self.packetsNSH[nshIndex]
		nshHeader[8:] = nshCI
		self.packetsNSH[nshIndex] = nshHeader
		return '0'

	#============== NSHP SERVERS ==============

	def nshpRemovalServer(self):

		while True:
			if self.remInputArray:
				self.remInSharedLock.acquire()
				pkt = self.remInputArray.pop(0)
				self.remInSharedLock.release()
				pkt = self.nshpRemoval(pkt)		
				self.remOutSharedLock.acquire()
				self.remOutputArray.append(pkt)
				self.remOutSharedLock.release()
			
	def nshpReinsertServer(self):

		while True:
			if self.reiInputArray:
				self.reiInSharedLock.acquire()
				pkt = self.reiInputArray.pop(0)
				self.reiInSharedLock.release()
				pkt = self.nshpReinsert(pkt)
				self.reiOutSharedLock.acquire()
				self.reiOutputArray.append(pkt)
				self.reiOutSharedLock.release()
			
	def nshpUpdateServer(self):

		run(host='localhost', port=6666, debug=True)

	def nshpStart(self):

		self.processRem = multiprocessing.Process(target=self.nshpRemovalServer, args=())
		self.processRem.start()
		self.processRei = multiprocessing.Process(target=self.nshpReinsertServer, args=())
		self.processRei.start()
		#self.processUpd = multiprocessing.Process(target=self.nshpUpdateServer)
		#self.processUpd.start()

	def nshpStop(self):

		self.processRem.terminate()
		self.processRei.terminate()
		#self.processUpd.terminate()

#============== NSHP TEST ==============

# nshpInstance = NSHProcessor()
# nshpInstance.nshpStart()

# while True:
# 	userInput = input('Input: ')
# 	if userInput == 'end':
# 		nshpInstance.nshpStop()
# 		break
# 	if userInput == 'send':
# 		pkt = sniff(count = 1)
# 		pkt = bytearray(bytes(pkt[0]))
# 		fakeNSH = bytearray(bytes([x for x in range(1,25)]))
# 		pkt = pkt[0:14] + fakeNSH + pkt[14:]
# 		print (pkt)
# 		nshpInstance.remInSharedLock.acquire()
# 		nshpInstance.remInputArray.append(pkt)
# 		nshpInstance.remInSharedLock.release()
# 	if userInput == 'change':
# 		nshpInstance.remInSharedLock.acquire()
# 		pkt = nshpInstance.remOutputArray.pop(0)
# 		nshpInstance.remInSharedLock.release()
# 		nshpInstance.reiInSharedLock.acquire()
# 		nshpInstance.reiInputArray.append(pkt)
# 		nshpInstance.reiInSharedLock.release()
# 	if userInput == 'print1':
# 		print (nshpInstance.remOutputArray)
# 	if userInput == 'print2':
# 		print (nshpInstance.reiOutputArray)
		
#==================================================