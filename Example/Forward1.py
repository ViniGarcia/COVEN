import sys
import socket
import atexit
import signal
import multiprocessing

class Forward:

	variableManager = None
	processedPackets = None

	fromIR = None
	toIR = None

	eaConnection = None


	def __init__(self):

		self.variableManager = multiprocessing.Manager()
		self.processedPackets = self.variableManager.Value('i', 0)

	def extendedAgent(self):

		self.eaConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.eaConnection.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
		self.eaConnection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.eaConnection.bind(('localhost', 8021))
		self.eaConnection.listen(1)

		signal.signal(signal.SIGTERM, self.eaTerminate)
		signal.signal(signal.SIGINT, self.eaTerminate)

		while(True):
			clientSocket, clientAddress = self.eaConnection.accept()

			request = clientSocket.recv(1500) #REQUEST MAXIMUM SIZE
			if request.decode('utf-8') == "PP":
				clientSocket.send(bytes(str(self.processedPackets.value), 'utf-8'))
			else:
				clientSocket.send(bytes("INVALID REQUEST!!", 'utf-8'))

			clientSocket.close()

	def networkFunction(self):

		self.fromIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.fromIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
		self.fromIR.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.fromIR.bind(('localhost', 8010))
		self.fromIR.listen(1)
		fromIRConnection, clientData = self.fromIR.accept()

		self.toIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.toIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
		self.toIR.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.toIR.connect(('localhost', 8011))

		while True:
			pkt = fromIRConnection.recv(1514)
			self.processedPackets.value += 1
			print ('OK2!!')
			self.toIR.send(pkt)

	def nfTerminate(self, arg1, arg2):

		try:
			self.fromIR.shutdown(socket.SHUT_RDWR)
			self.toIR.shutdown(socket.SHUT_RDWR)
		except:
			pass
			
		self.fromIR.close()
		self.toIR.close()
		sys.exit()

	def eaTerminate(self, arg1, arg2):

		self.eaConnection.shutdown(socket.SHUT_RDWR)
		self.eaConnection.close()
		sys.exit()

	def main(self):

		try:
			#eaProcess = multiprocessing.Process(target=self.extendedAgent, args=())
			#eaProcess.start()
			self.networkFunction()
		finally:
			pass
			#eaProcess.terminate()

nfInstance = Forward()
signal.signal(signal.SIGTERM, nfInstance.nfTerminate)
signal.signal(signal.SIGINT, nfInstance.nfTerminate)
nfInstance.main()

