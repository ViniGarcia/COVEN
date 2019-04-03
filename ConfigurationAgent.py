import yaml
import time
import sys
from bottle import route, run, request

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

@route('/status/', method='GET')
def platformStatus():

	global platformOn

	if platformOn:
		return 'On'
	else:
		return 'Off'

@route('/configure/', method='POST')
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

@route('/start/', method='POST')
def platformStart():

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

@route('/stop/', method='POST')
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

@route('/reset/', method='POST')
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

@route('/off/', method='POST')
def platformOff():

	global platformOn

	if platformOn:
		return "-1"

	sys.stderr.close()

run(host='localhost', port=6667, debug=True)