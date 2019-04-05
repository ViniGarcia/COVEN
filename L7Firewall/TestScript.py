import yaml
import sys
from requests import get, post, put

if len(sys.argv) != 2:
	print("Execution: python3 TestScript.py <yaml_file>")
	sys.exit()

exampleFile = open(sys.argv[1], 'r')
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
