#==================================================

import multiprocessing
import subprocess
from bottle import route, run, request
from requests import get

#============== MA CLASS ==============

class ManagementAgent:

    #============== MA ATTRIBUTES ==============

    maComponentsPorts = None
    maComponentsSockets = None
    maComponentsRequests = None

    maProcess = None

    #componentPorts = dictionary with file name as key containing a tuple
    #                 -> [0]: input port
    #                 -> [1]: output port
    #componentsSockets = dictionarty with file name as key containining
    #                    the EA socket port.
    #componentsRequest = dictionarty with file name as key containining
    #                    the EA operations dictionary which, in turn,
    #                    contains the request ID and its operation message.
    def __init__(self, componentsPorts, componentsSockets, componentRequests):

        self.maComponentsPorts = componentsPorts
        self.maComponentsSockets = componentsSockets
        self.maComponentsRequests = componentRequests

    #=============== MA METHODS ===============

    def maList(self):
        listString = "\n---- AVAILABLE OPERATIONS ----\n\n"
        listString += "list: show this\n"
        listString += "check: check the components in and out connections\n"
        listString += "request [file] [request]: ask for the component of [file] for the data of [request]\n"

        listString += "\n---- AVAILABLE REQUESTS ----\n\n"

        for ea in self.maComponentsRequests:
            listString += " -> [file]: " + ea + "\n"
            for op in self.maComponentsRequests[ea]:
                listString += "  - [request]: " + op + "\n"
            listString += "\n"

        listString += "--------------------------------\n"
        return listString

    def maCheck(self):

        results = "\n---- CHECK SUMMARY ----\n\n"

        for component in self.maComponentsPorts:
            results += "-> " + component + "\n"

            for port in self.maComponentsPorts[component]:
                checkResult = ''
                process = subprocess.Popen(['nc', '-vz', 'localhost', str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                pResult, pError = process.communicate()
                pResult = pResult.decode('utf8')

                if "refused" in pResult:
                    results += "  - " + str(port) + ": failure\n"
                else:
                    if "open" in pResult:
                        results += "  - " + str(port) + ": success\n"
                    else:
                        results += "  - " + str(port) + ": error\n"
            results += "\n"

        results += "-----------------------"
        return results

    def maRequest(self, rFile, rRequest):
        print(rFile)
        print(rRequest)
        return 0

    #=============== MA SERVERS ===============

    def maServer(self):

        route('/ma/list', callback = self.maList)
        route('/ma/check', callback = self.maCheck)
        route('/ma/request/<rFile>/<rRequest>', callback = self.maRequest)
        run(host='localhost', port = 6668, debug = True)

    def maStart(self):

        self.maProcess = multiprocessing.Process(target=self.maServer)
        self.maProcess.start()

    def maStop(self):

        self.maProcess.terminate()

    #=============== MA TEST ===============

maInstance = ManagementAgent({"comp1":(6668, 8001), "comp2":(8002, 8003)}, {"comp1":8004, "comp2":8005}, {"comp1":{"lala":"lalaaction", "lele":"leleaction"}, "comp2":{"lulu":"luluaction"}})
maInstance.maStart()

while True:
    userInput = input('Input: ')
    if userInput == 'end':
    	maInstance.maStop()
    	break
    if userInput == 'list':
        response = get('http://localhost:6668/ma/list')
        print(response.text)
    if userInput == 'check':
        response = get('http://localhost:6668/ma/check')
        print(response.text)
    if userInput == 'request':
        response = get('http://localhost:6668/ma/request/comp1/lala')
        print(response.text)


#==================================================
