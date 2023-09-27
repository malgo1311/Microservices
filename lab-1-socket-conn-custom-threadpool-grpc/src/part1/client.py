#!/usr/bin/env python3
import socket
import json
import time
from setup import *

counter = 0
while True:
	for input_search in ['Hello World', 'hey', 'GameStart', 'FishCo']:

		counter += 1

		s = socket.socket()

		# connect to server
		s.connect((HOST, PORT))

		logger.debug(f"")
		logger.debug(f"New socket connection established")
		# send lookup query to server
		data = {"methodName": "Lookup", 
				"arguments": {"stockName": input_search}
				}
		message_string = json.dumps(data)	# serialize query

		start = time.time() # to calculate latency
		logger.debug(f"Sending msg to server")
		s.send(message_string.encode())

		# receive message from server
		message_from_server = (s.recv(1024)).decode("utf-8")
		end = time.time()

		if "methodName not found" in message_from_server:
			display_message = message_from_server
		else:
			display_message = f"Stock price of {input_search} is {message_from_server}"

		logger.info(f"Time {end-start:.10f} sec ; From server: {counter} {display_message}")

		# close the connection
		s.close()
		logger.debug(f"Request complete")

	if counter >= QUERYCOUNT: break