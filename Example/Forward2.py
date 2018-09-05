import socket

fromIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fromIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
fromIR.bind(('localhost', 8012))
fromIR.listen(1)
fromIRConnection, clientData = fromIR.accept()

toIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
toIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
toIR.connect(('localhost', 8013))

while True:
	pkt = fromIRConnection.recv(1514)
	print ('OK2!!')
	toIR.send(pkt)