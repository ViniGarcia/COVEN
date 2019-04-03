import yaml
from requests import get, post, put

exampleFile = open('Example.yaml', 'r')
fileData = exampleFile.read()
yamlData = yaml.parse(exampleFile.read())
exampleFile.close()

while True:
	userInput = input('Input: ')
	if userInput == 'status':
		response = get('http://localhost:6667/status/')
		print (response.text)
	if userInput == 'configure':
		response = post('http://localhost:6667/configure/', data = fileData)
		print (response.text)
	if userInput == 'start':
		response = post('http://localhost:6667/start/')
		print (response.text)
	if userInput == 'stop':
		response = post('http://localhost:6667/stop/')
		print (response.text)
	if userInput == 'reset':
		response = post('http://localhost:6667/reset/')
		print (response.text)
	if userInput == 'off':
		response = post('http://localhost:6667/off/')
		print (response.text)
	if userInput == 'end':
		break

	if userInput == 'list':
	    response = get('http://localhost:6668/ma/list')
	    print(response.text)
	if userInput == 'check':
	    response = get('http://localhost:6668/ma/check')
	    print(response.text)
	if userInput == 'request1':
	    response = get('http://localhost:6668/ma/request/Forward.java/Packets')
	    print(response.text)
	if userInput == 'request2':
	    response = get('http://localhost:6668/ma/request/Forward1.py/Packets')
	    print(response.text)
	if userInput == 'request3':
	    response = get('http://localhost:6668/ma/request/Forward2.py/Packets')
	    print(response.text)
	if userInput == 'request4':
	    response = get('http://localhost:6668/ma/request/Forward.cli/Packets')
	    print(response.text)
