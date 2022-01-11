##!/bin/env python	# ignore
# coding: utf-8
import os
import json
from time import sleep
from bottle import route, run, request, HTTPResponse, template, static_file

@route('/static/:path#.+#', name='static')
def static(path):
    	print(2)
	return static_file(path, root='static')

@route('/')
def root():
    	print(3)
	return template("index")

# curl -H "Accept: application/json" -H "Content-type: application/json" -X POST -d '{"LED0":"ON", "LED1":"ON", "LED2":"ON", "LED3":"ON", "LED4":"ON", "COLOR0_r":100, "COLOR0_g":100, "COLOR0_b":100, "COLOR1_r":100, "COLOR1_g":100, "COLOR1_b":100}' http://192.168.1.87:8080/setStatus
@route('/setStatus', method='POST')
def setStatusEntry():
    	print(4)
	var = request.json
	print (var)

	# Retrieve commands for PL device (to be sent to C application)
	cmdPL = var["LED0"] + "," + var["LED1"] + "," + var["LED2"] + "," + var["LED3"]
	print(cmdPL)
	sendPipe(cmdPL)

	# Retrieve command for PS device (only LED4(PS GPIO))
	gpioPS = open("/sys/class/gpio/gpio913/value", "w")
	if(var["LED4"] == "ON"):
		gpioPS.write("1")
	elif(var["LED4"] == "OFF"):
		gpioPS.write("0")
	else:
		print("error")

	#print(gpioPS)

	

	

	retBody = {"ret": "ok"}
	r = HTTPResponse(status=200, body=retBody)
	r.set_header('Content-Type', 'application/json')
	return r

# curl -H "Accept: application/json" -H "Content-type: application/json" -X POST -d '{"dummy":"0"}' http://192.168.1.2:8080/getStatus
@route('/getStatus', method='POST')
def getStatusEntry():
    #print(5)
	statusJson = json.loads(recvPipe())
	print(statusJson)
	
	#get temperature sensor data from LM-35
	tempraw = open("/sys/bus/iio/devices/iio:device1/in_voltage8_vaux7_raw","r")
	temprawint = float(tempraw.read())
	tempvolt = ((temprawint / 4096)*100)
	#attach temperature data to JSON string 
	tempstr = {"temp": tempvolt}
	statusJson.update(tempstr)
	val = statusJson
	
	
	print(tempstr)
	tempraw.close()
	
	retBody = {"ret": "ok"}
	retBody.update(val)
	print(retBody)

	r = HTTPResponse(status=200, body=retBody)
	r.set_header('Content-Type', 'application/json')
	return r

def sendPipe(sendPipe):
    	print(6)
	#send data to CPP code to set LEDs
	pipeP2C = open("/home/root/pipe_p2c", "w")
	# pipeP2C.write("ON,OFF,ON,OFF,100,100,100,100,100,100")
	pipeP2C.write(sendPipe)
	pipeP2C.close()

def recvPipe():
    	print(7)
	#receive data form CPP code to communicate with web server
	pipeC2P = open("/home/root/pipe_c2p", "r")
	statusJson = pipeC2P.read()
	pipeC2P.close()
	print(statusJson)
	return statusJson





def setupPSGPIO():
    	print(8)
	# LED4
	if(not os.path.exists("/sys/class/gpio/gpio913")):
		gpioPS = open("/sys/class/gpio/export", "w")
		gpioPS.write("913")
		sleep(2)
		gpioPS.close()
	gpioPS = open("/sys/class/gpio/gpio913/direction", "w")
	gpioPS.write("out")
	gpioPS.close()

	if(not os.path.exists("/sys/bus/iio/devices/iio:device1/in_voltage8_vaux7_raw")):
    		tempraw = open()



def main():
    	print(1)
	print("Hello")
	while(not (os.path.exists("/home/root/pipe_p2c") and os.path.exists("/home/root/pipe_c2p"))):
		sleep(1)
	#start server
	setupPSGPIO()
	print('Server Start')
	run(host='192.168.1.2', port=8080, debug=True, reloader=True)
	# run(host='0.0.0.0', port=8080, debug=False, reloader=False)

if __name__ == '__main__':
	main()
