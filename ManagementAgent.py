#==================================================

import multiprocessing
import subprocess
import socket
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

        if not rFile in self.maComponentsSockets:
            return "ERROR: INVALID FILE!!"
        if not rRequest in self.maComponentsRequests[rFile]:
            return "ERROR: INVALID REQUEST!!"

        serverConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverConnection.settimeout(4.0)
        try:
            serverConnection.connect(('localhost', self.maComponentsSockets[rFile]))
        except:
            serverConnection.close()
            return "ERROR: COULD NOT CONNECT THE EXTEND AGENT!!"

        serverConnection.send(bytes(self.maComponentsRequests[rFile][rRequest], 'utf8'))
        try:
            answer = serverConnection.recv(3028) #REQUESTS ANSWER MAXIMUM SIZE
        except:
            serverConnection.close()
            return "ERROR: THE EXTEND AGENT DID NOT ANSWER!!"

        serverConnection.close()
        return answer

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

# maInstance = ManagementAgent({"Forward.java":(8008, 8009), "Forward1.py":(8010, 8011), "Forward2.py":(8012, 8013), "Forward.cli":(8014, 8015)}, {"Forward.java":8020, "Forward1.py":8021, "Forward2.py":8022, "Forward.cli":8023}, {"Forward.java":{"Packets":"PP"}, "Forward1.py":{"Packets":"PP"}, "Forward2.py":{"Packets":"PP"}, "Forward.cli":{"Packets":"READ packages\n"}})
# maInstance.maStart()
#
# while True:
#     userInput = input('Input: ')
#     if userInput == 'end':
#     	maInstance.maStop()
#     	break
#     if userInput == 'list':
#         response = get('http://localhost:6668/ma/list')
#         print(response.text)
#     if userInput == 'check':
#         response = get('http://localhost:6668/ma/check')
#         print(response.text)
#     if userInput == 'request1':
#         response = get('http://localhost:6668/ma/request/Forward.java/Packets')
#         print(response.text)
#     if userInput == 'request2':
#         response = get('http://localhost:6668/ma/request/Forward1.py/Packets')
#         print(response.text)
#     if userInput == 'request3':
#         response = get('http://localhost:6668/ma/request/Forward2.py/Packets')
#         print(response.text)
#     if userInput == 'request4':
# 	    response = get('http://localhost:6668/ma/request/Forward.cli/Packets')
# 	    print(response.text)

#==================================================
#Socket(TCP,127.0.0.1,8015)
