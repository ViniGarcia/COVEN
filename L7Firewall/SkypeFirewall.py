import socket
from scapy.all import *
from datetime import datetime

fromIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fromIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
fromIR.bind(('localhost', 8012))
fromIR.listen(1)
fromIRConnection, clientData = fromIR.accept()

toIR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
toIR.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1514)
toIR.connect(('localhost', 8013))

log = open("skype_firewall.log",'w')

while True:
    pkt = fromIRConnection.recv(1514)
    #Some WLAN packets cannot be parsed to Ethernet
    try:
        et = Ether(pkt)
    except:
        log.write("[%s] - Error reading bytes as Ethernet\n" % datetime.now())

    if IP in et:
        dropFlag = False
        for opt in et[IP].options:
            if bytes(opt) == b'\x07\x03\x04':
                dropFlag = True
                log.write("[%s] - Marked packet has been dropped\n" % datetime.now())
                break;

        if not dropFlag:
            toIR.send(bytes(et))
    else:
        toIR.send(bytes(et))
