import socket
from scapy.all import *
from datetime import datetime

fromIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fromIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
fromIR.bind(('localhost', 8010))
fromIR.listen(1)
fromIRConnection, clientData = fromIR.accept()

toIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
toIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
toIR.connect(('localhost', 8011))

log = open("skype_dpi.log",'w')

while True:
	pkt = fromIRConnection.recv(1514)
	try:
		et = Ether(pkt)
	except:
		log.write("[%s] - Error reading bytes as Ethernet" % datetime.now())
		continue

	if not IP in et:
		toIR.send(bytes(et))
		continue

	#UDP packets with a payload size of 18 bytes and the third byte of the payload set to 0x02 (U1).
	if UDP in et:
		if et[UDP].len == 18:
			del et[IP].ihl
			del et[IP].len
			del et[IP].chksum
			et[IP].options = IPOption_RR()
			toIR.send(bytes(et))
			log.write("[%s] - Marked possible UDP Skype packet\n" % datetime.now())
		else:
			toIR.send(bytes(et))
	#Rules for skype proto TCP
	elif TCP in et:
		if et[IP][TCP].dport == 443 and len(et[IP][TCP]) == 72:
			del et[IP].ihl
			del et[IP].len
			del et[IP].chksum
			et[IP].options = IPOption_RR()
			toIR.send(bytes(et))
			log.write("[%s] - Marked possible TCP Skype packet on port 443\n" % datetime.now())
		#Port 80 Operation
		elif et[IP][TCP].dport == 80:
			del et[IP].ihl
			del et[IP].len
			del et[IP].chksum
			et[IP].options = IPOption_RR()
			toIR.send(bytes(et))
			log.write("[%s] - Marked possible TCP Skype packet on port 80\n" % datetime.now())
		else:
			toIR.send(bytes(et))
	else:
		toIR.send(bytes(et))
