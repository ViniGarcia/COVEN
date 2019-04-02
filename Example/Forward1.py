import socket
import multiprocessing

class Forward:

	variableManager = None
	processedPackets = None

	def __init__(self):

		self.variableManager = multiprocessing.Manager()
		self.processedPackets = self.variableManager.Value('i', 0)


	def ExtendedAgent(self):

		clientConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientConnection.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
		clientConnection.bind(('localhost', 8021))
		clientConnection.listen(1)

		while(True):
			clientSocket, clientAddress = clientConnection.accept()

			request = clientSocket.recv(1500) #REQUEST MAXIMUM SIZE
			if request.decode('utf-8') == "PP":
				clientSocket.send(bytes(str(self.processedPackets.value), 'utf-8'))
			else:
				clientSocket.send(bytes("INVALID REQUEST!!", 'utf-8'))

			clientSocket.close()


	def NetworkFunction(self):

		fromIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		fromIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
		fromIR.bind(('localhost', 8010))
		fromIR.listen(1)
		fromIRConnection, clientData = fromIR.accept()

		toIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		toIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
		toIR.connect(('localhost', 8011))

		while True:
			pkt = fromIRConnection.recv(1514)
			print ('OK2!!')
			toIR.send(pkt)


	def main(self):

		eaProcess = multiprocessing.Process(target=self.ExtendedAgent, args=())
		eaProcess.start()
		self.NetworkFunction()

nfInstance = Forward()
nfInstance.main()
