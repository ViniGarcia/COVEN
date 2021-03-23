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

	return ManagementAgent(componentsPorts, componentsSockets, componentRequests, httpInterface)

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

def platformPackageCore(name, data):
	try:
		packageFile = open("./NFPackages/" + name + ".coven", "wb+")
		packageFile.write(data)
		packageFile.close()
	except:
		return "-8"

	return "0"

@httpInterface.route('/package/<name>/', method='POST')
def platformPackage(name):

		return platformPackageCore(name, request.body.read())

@httpInterface.route('/install/<name>/', method='POST')
def platformInstall(name):

	if not name + ".coven" in os.listdir("./NFPackages/"):
		return "-9"

	with zipfile.ZipFile("./NFPackages/" + name + ".coven", 'r') as zipPackage:
		extension = name.rfind(".")
		if extension > 0:
			name = name[:name.rfind(".")]
		if name in os.listdir("./NFPackages/"):
			shutil.rmtree("./NFPackages/" + name)
		os.mkdir("./NFPackages/" + name)
		zipPackage.extractall("./NFPackages/" + name)
		return "0"

@httpInterface.route('/setup/<name>/', method='POST')
def platformSetup(name):

	response = platformPackageCore(name, request.body.read())
	if response != "0":
		return response
	return platformInstall(name)

def platformConfCore(confYAML):

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

@httpInterface.route('/configure/', method='POST')
def platformConf():

	return platformConfCore(request.body.read())


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
	maInstance.maStart()
	time.sleep(0.500)
	if nshpInstance != False:
		nshpInstance.nshpStart()
		time.sleep(0.500)
	irInstance.irModulesStart()
	platformOn = True

	return "0"

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
	maInstance.maStop()
	vnsInstance.vnsStop()
	if nshpInstance != False:
		nshpInstance.nshpStop()
	ppsInstace.ppsStop()

	platformOn = False

	return "0"

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

	irInstance.irReset()

	ppsInstace = None
	vnsInstance = None
	nshpInstance = None
	maInstance = None
	irInstance = None

	return "0"

@httpInterface.route('/off/', method='POST')
def platformOff():

	global platformOn
	global interfaceIP
	global httpServer

	if platformOn:
		return "-1"

	closeSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	closeSocket.sendto("close".encode("utf-8"), (interfaceIP, 6668))
	closeSocket.close()

	httpServer.stop()

	return "0"

# ###################################### SOCKET BASIC INTERFACE #######################################

def socketPackage(socketAgent, fileName, fileSize):

	filePackage = open("./NFPackages/" + fileName + ".coven", "wb+")
	fileReceived = 0
	while fileReceived < fileSize:
		data, client = socketAgent.recvfrom(1024)
		filePackage.write(data)
		fileReceived = fileReceived + len(data)
	filePackage.close()
	return 0

def socketAgent(interfaceIP):
	print("SOCKET INTERFACE IS RUNNING AT " + interfaceIP + ":6668\n")
	socketConnector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socketConnector.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	socketConnector.bind((interfaceIP, 6668))
	socketConnector.listen(1)

	def packageFunction(packageName, packageSize):
		try:
			response = socketPackage(socketAgent, packageName, int(packageSize))
			if not response:
				return "200|SUCCESFULLY EXECUTED THE PACKAGE OPERATION"
		except Exception as e:
			return "400|AN ERROR OCCURRED DURING THE PACKAGE OPERATION (" + str(e) + ")"

	def installFunction(packageName):
		try:
			with zipfile.ZipFile("./NFPackages/" + packageName + ".coven", 'r') as zipPackage:
				extension = packageName.rfind(".")
				if extension > 0:
					packageName = packageName[:packageName.rfind(".")]
				if packageName in os.listdir("./NFPackages/"):
					shutil.rmtree("./NFPackages/" + packageName)
				os.mkdir("./NFPackages/" + packageName)
				zipPackage.extractall("./NFPackages/" + packageName)
				return "200|SUCCESFULLY EXECUTED THE INSTALL OPERATION" 
		except Exception as e:
			return "400|AN ERROR OCCURRED DURING THE INSTALL OPERATION (" + str(e) + ")"

	while True:
		socketAgent, socketAddress = socketConnector.accept()
		request = socketAgent.recv(1024)
		try:
			request = request.decode()
		except:
			socketAgent.sendall("400|AN ERROR OCCURRED DURING THE REQUEST".encode())
			socketAgent.close()
			continue

		print(socketAddress, "- -", "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "]", "\"SOCK REQ " + request + "\"")

		if request.startswith("package"):
			try:
				data = request.split("|")
				if len(data) != 3:
					socketAgent.sendall("400|AN ERROR OCCURRED DURING THE PACKAGE OPERATION (Invalid arguments)".encode())
					socketAgent.close()
					continue
				if not data[2].isdigit():
					socketAgent.sendall("400|AN ERROR OCCURRED DURING THE PACKAGE OPERATION (Ivalid digit)".encode())
					socketAgent.close()
					continue
				socketAgent.sendall(packageFunction(data[1], data[2]).encode())
			except Exception as e:
				socketAgent.sendall(("400|AN ERROR OCCURRED DURING THE PACKAGE OPERATION (" + str(e) + ")").encode())

		elif request.startswith("install"):
			try:
				data = request.split("|")
				if len(data) != 2:
					socketAgent.sendall("400|AN ERROR OCCURRED DURING THE INSTALL OPERATION (Invalid arguments)".encode())
					socketAgent.close()
					continue
				if not data[1] + ".coven" in os.listdir("./NFPackages/"):
					socketAgent.sendall("400|AN ERROR OCCURRED DURING THE INSTALL OPERATION (Ivalid package)".encode())
					socketAgent.close()
					continue
				socketAgent.sendall(installFunction(data[1]).encode())
			except Exception as e:
				socketAgent.sendall(("400|AN ERROR OCCURRED DURING THE INSTALL OPERATION (" + str(e) + ")").encode())

		elif request.startswith("setup"):
			try:
				data = request.split("|")
				if len(data) != 3:
					socketAgent.sendall("400|AN ERROR OCCURRED DURING THE SETUP OPERATION (Invalid arguments)".encode())
					socketAgent.close()
					continue
				if not data[2].isdigit():
					socketAgent.sendall("400|AN ERROR OCCURRED DURING THE SETUP OPERATION (Ivalid digit)".encode())
					socketAgent.close()
					continue
				response = packageFunction(data[1], data[2])
				if not response.startswith("200"):
					socketAgent.sendall(response.encode())
					socketAgent.close()
					continue
				socketAgent.sendall(installFunction(data[1]).encode())
			except Exception as e:
				socketAgent.sendall(("400|AN ERROR OCCURRED DURING THE SETUP OPERATION (" + str(e) + ")").encode())

		elif request.startswith("configure"):
			try:
				data = request.split("|")
				if len(data) != 2:
					socketAgent.sendall("400|AN ERROR OCCURRED DURING THE CONFIGURE OPERATION (Invalid arguments)".encode())
					socketAgent.close()
					continue
				extension = data[1].rfind(".")
				if extension > 0:
					data[1] = data[1][:data[1].rfind(".")]
				if not data[1] in os.listdir("./NFPackages/"):
					socketAgent.sendall("400|AN ERROR OCCURRED DURING THE CONFIGURE OPERATION (Ivalid package)".encode())
					socketAgent.close()
					continue
				yamlFile = open("./NFPackages/" + data[1] + "/Scripts/install.yaml", "r")
				response = requests.post('http://' + interfaceIP + ':6667/configure/', data=yamlFile.read())
				socketAgent.sendall((str(response.status_code) + "|" + response.text).encode())
			except Exception as e:
				socketAgent.sendall(("400|AN ERROR OCCURRED DURING THE CONFIGURE OPERATION (" + str(e) + ")").encode())

		elif request == "start":
			response = requests.post('http://' + interfaceIP + ':6667/start/')
			socketAgent.sendall((str(response.status_code) + "|" + response.text).encode())

		elif request == "stop":
			response = requests.post('http://' + interfaceIP + ':6667/stop/')
			socketAgent.sendall((str(response.status_code) + "|" + response.text).encode())

		elif request == "reset":
			response = requests.post('http://' + interfaceIP + ':6667/reset/')
			socketAgent.sendall((str(response.status_code) + "|" + response.text).encode())

		elif request == "status":
			response = requests.get('http://' + interfaceIP + ':6667/status/')
			socketAgent.sendall((str(response.status_code) + "|" + response.text).encode())

		elif request == "list":
			response = requests.get('http://' + interfaceIP + ':6667/ma/list')
			socketAgent.sendall((str(response.status_code) + "|" + response.text).encode())

		elif request == "check":
			response = requests.get('http://' + interfaceIP + ':6667/ma/check')
			socketAgent.sendall((str(response.status_code) + "|" + response.text).encode())

		elif request.startswith("request"):
			try:
				data = request.split("|")
				if len(data) != 4:
					socketAgent.sendall("400|AN ERROR OCCURRED DURING THE REQUEST OPERATION (Invalid arguments)".encode())
					socketAgent.close()
					continue
				response = requests.get('http://' + interfaceIP + ':6667/ma/request/' + data[1] + '/' + data[2], data = data[3])
				socketAgent.sendall((str(response.status_code) + "|" + response.text).encode())
			except Exception as e:
				socketAgent.sendto("400|AN ERROR OCCURRED DURING THE REQUEST OPERATION (" + str(e) + ")".encode())

		elif request == "off":
			response = requests.post('http://' + interfaceIP + ':6667/off/')
			socketAgent.sendall((str(response.status_code) + "|" + response.text).encode())
			socketAgent.close()
			break

		elif request == "close":
			response = socketAgent.sendall("200|SUCCESFULLY EXECUTED THE CLOSING OPERATION".encode())
			socketAgent.close()
			break

		socketAgent.close()

# ###################################### RUNNING ENVIRONMENT #######################################

socketInterface = Process(target=socketAgent, args=(interfaceIP,))
socketInterface.start()
httpInterface.run(server=httpServer, debug=True)
