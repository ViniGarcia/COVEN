import os
import sys
import yaml
import time
import socket
import shutil
import zipfile
import requests
import datetime

from multiprocessing import Process
from bottle import route, run, request, Bottle, ServerAdapter

from PProcSubsystem import PProcSubsystem
from VNetSubsystem import VNetSubsystem
from NSHProcessor import NSHProcessor
from InternalRouter import InternalRouter
from ManagementAgent import ManagementAgent

platformOn = False
ppsInstace = None
vnsInstance = None
nshpInstance = None
irInstance = None
maInstance = None

# ###################################### BOTTLE SERVER #######################################

class ConfAgentServer(ServerAdapter):
    server = None

    def run(self, handler):

        from wsgiref.simple_server import make_server, WSGIRequestHandler

        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
    	self.server.server_close()

if len(sys.argv) != 2:
	print("USAGE: *.py MANAGEMENT_IP")
	exit(0)

try:
	socket.inet_aton(sys.argv[1])
except:
	print("ERROR: INVALID IP ADDRESS PROVIDED")
	exit(0)

interfaceIP = sys.argv[1]

httpInterface = Bottle()
httpServer = ConfAgentServer(host=interfaceIP, port=6667)

# ###################################### CONFIGURATION FUNCTIONS #######################################

def createPPS(dictYAML):

	requestTuples = []

	if not 'PPS' in dictYAML:
		return None
	for request in dictYAML['PPS']:
		if not 'Framework' in request or not 'NFs' in request:
			return None
		for subrequest in request['NFs']:
			if not 'File' in subrequest or not 'Input' in subrequest or not 'Output' in subrequest or not 'Order' in subrequest:
				return None

			if not 'Arguments' in subrequest:
				requestTuples.append((request['Framework'], subrequest['File'], None))
			else:
				requestTuples.append((request['Framework'], subrequest['File'], subrequest['Arguments']))

	return PProcSubsystem(requestTuples)

def createVNS(dictYAML):

	if not 'VNS' in dictYAML:
		return None
	if not 'Tool' in dictYAML['VNS'] or not 'Input' in dictYAML['VNS'] or not 'Output' in dictYAML['VNS']:
		return None

	return VNetSubsystem(dictYAML['VNS']['Tool'], dictYAML['VNS']['Input'], dictYAML['VNS']['Output'])

def createNSHP(dictYAML):

	if not 'NSHP' in dictYAML:
		return None

	if dictYAML['NSHP']:
		return NSHProcessor()
	else:
		return False

def createMA(dictYAML):

	if not 'PPS' in dictYAML:
		return None
	if len(dictYAML['PPS']) == 0:
		return None

	componentsPorts = {}
	componentsSockets = {}
	componentRequests = {}

	for request in dictYAML['PPS']:
		if not 'NFs' in request:
			return None

		for netFunction in request['NFs']:
			if not 'File' in netFunction:
				return None
			if not 'Input' in netFunction:
				return None
			if not 'Output' in netFunction:
				return None

			nfName = netFunction['File'].split('/')[-1]
			componentsPorts[nfName] = (netFunction['Input'], netFunction['Output'])

			if not 'EMA' in netFunction:
				continue
			if not 'Port' in netFunction['EMA']:
				return None

			componentsSockets[nfName] = netFunction['EMA']['Port']

			if not 'Requests' in netFunction['EMA']:
				return None

			for operation in netFunction['EMA']['Requests']:
				netFunction['EMA']['Requests'][operation] = netFunction['EMA']['Requests'][operation].replace('\\n', '\n')
			componentRequests[nfName] = netFunction['EMA']['Requests']

	return ManagementAgent(componentsPorts, componentsSockets, componentRequests)

def createIR(dictYAML, vnsInstance, nshpInstance):

	orderedDict = {}
	orderedPorts = []
	for request in dictYAML['PPS']:
		for subrequest in request['NFs']:
			orderedDict[subrequest['Order']] = (subrequest['Input'], subrequest['Output'])

	#Ordering begins in 1
	for index in range(1, len(orderedDict)+1):
		orderedPorts.append(orderedDict[index])

	return InternalRouter(vnsInstance, nshpInstance, orderedPorts)

# ###################################### HTTP INTERFACE #######################################

@httpInterface.route('/status/', method='GET')
def platformStatus():

	global platformOn

	if platformOn:
		return 'On'
	else:
		return 'Off'

@httpInterface.route('/configure/', method='POST')
def platformConf():

	global platformOn
	global ppsInstace
	global vnsInstance
	global nshpInstance
	global maInstance
	global irInstance

	if platformOn:
		return "-1"
	if ppsInstace != None:
		return "-2"

	confYAML = request.body.read()
	try:
		dictYAML = yaml.safe_load(confYAML)
	except:
		return "-3"

	ppsInstace = createPPS(dictYAML)
	if ppsInstace == None:
		return "-4"
	vnsInstance = createVNS(dictYAML)
	if vnsInstance == None:
		ppsInstace = None
		return "-5"
	nshpInstance = createNSHP(dictYAML)
	if nshpInstance == None:
		vnsInstance = None
		ppsInstace = None
		return "-6"
	maInstance = createMA(dictYAML)
	if maInstance == None:
		nshpInstance = None
		vnsInstance = None
		ppsInstace = None
		return "-7"

	if nshpInstance != False:
		irInstance = createIR(dictYAML, vnsInstance, nshpInstance)
	else:
		irInstance = createIR(dictYAML, vnsInstance, None)

	return "0"

@httpInterface.route('/start/', method='POST')
def platformStart():

	global platformOn
	global ppsInstace
	global vnsInstance
	global nshpInstance
	global maInstance
	global irInstance

	global interfaceIP

	if platformOn:
		return "-1"
	if ppsInstace == None:
		return "-2"

	irInstance.irNetworkStart()
	time.sleep(0.500)
	ppsInstace.ppsStart()
	time.sleep(1.000)
	vnsInstance.vnsStart()
	time.sleep(0.500)
	maInstance.maStart(httpInterface)
	time.sleep(0.500)
	if nshpInstance != False:
		nshpInstance.nshpStart()
		time.sleep(0.500)
	irInstance.irModulesStart()
	platformOn = True

@httpInterface.route('/stop/', method='POST')
def platformStop():

	global platformOn
	global ppsInstace
	global vnsInstance
	global nshpInstance
	global maInstance
	global irInstance

	if not platformOn:
		return "-1"

	irInstance.irStop()
	maInstance.maStop(httpInterface)
	vnsInstance.vnsStop()
	if nshpInstance != False:
		nshpInstance.nshpStop()
	ppsInstace.ppsStop()

	platformOn = False

@httpInterface.route('/reset/', method='POST')
def platformReset():

	global platformOn
	global ppsInstace
	global vnsInstance
	global nshpInstance
	global maInstance
	global irInstance

	if platformOn:
		return "-1"
	if ppsInstace == None:
		return "-2"

	ppsInstace = None
	vnsInstance = None
	nshpInstance = None
	maInstance = None
	irInstance = None

@httpInterface.route('/off/', method='POST')
def platformOff():
	
	global platformOn
	global interfaceIP
	global httpServer

	if platformOn:
		return "-1"

	closeSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	closeSocket.sendto("close".encode("utf-8"), (interfaceIP, 12345))
	closeSocket.close()

	httpServer.stop()

# ###################################### SOCKET BASIC INTERFACE #######################################

def socketPackage(socketAgent, fileName, fileSize):
	
	filePackage = open("./NFPackages/" + fileName, "wb+")
	fileReceived = 0
	while fileReceived < fileSize:
		data, client = socketAgent.recvfrom(1024)
		filePackage.write(data)
		fileReceived = fileReceived + len(data)
	filePackage.close()
	return 0

def socketAgent(interfaceIP):
	print("SOCKET INTERFACE IS RUNNING AT " + interfaceIP + ":12345\n")
	socketAgent = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socketAgent.bind((interfaceIP, 12345))

	while True:
		request, client = socketAgent.recvfrom(1024)
		request = request.decode("utf-8")
		print(client[0], "- -", "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "]", "\"SOCK REQ " + request + "\"")

		if request.startswith("package"):
			data = request.split("|")
			if len(data) != 3:
				continue
			if not data[2].isdigit():
				continue
			response = socketPackage(socketAgent, data[1], int(data[2]))
		
		elif request.startswith("install"):
			data = request.split("|")
			if len(data) != 2:
				continue
			if not data[1] in os.listdir("./NFPackages/"):
				continue
			with zipfile.ZipFile("./NFPackages/" + data[1], 'r') as zipPackage:
				folderName = data[1][:data[1].rfind(".")]
				if folderName in os.listdir("./NFPackages/"):
					shutil.rmtree("./NFPackages/" + folderName)
				os.mkdir("./NFPackages/" + folderName)
				zipPackage.extractall("./NFPackages/" + folderName)
			yamlFile = open("./NFPackages/" + folderName + "/Scripts/install.yaml", "r")
			response = requests.post('http://' + interfaceIP + ':6667/configure/', data=yamlFile.read())
		
		elif request == "start":
			response = requests.post('http://' + interfaceIP + ':6667/start/')
		
		elif request == "stop":
			response = requests.post('http://' + interfaceIP + ':6667/stop/')
		
		elif request == "off":
			response = requests.post('http://' + interfaceIP + ':6667/off/')
			socketAgent.close()
			break

		elif request == "close":
			socketAgent.close()
			break			

# ###################################### RUNNING ENVIRONMENT #######################################

socketInterface = Process(target=socketAgent, args=(interfaceIP,))
socketInterface.start()
httpInterface.run(server=httpServer, debug=True)