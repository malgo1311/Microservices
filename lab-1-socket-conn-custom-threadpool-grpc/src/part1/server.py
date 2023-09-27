#!/usr/bin/env python3
import sys
import socket

from setup import *
from process import Threadpool, request_q

# initializing the threadpool
logger.info(f"Starting threadpool")
tp = Threadpool(NUM_OF_THREADS)

# setting up server side socket
s = socket.socket()
host = socket.gethostname()  # Get local machine name
logger.info(f"Server starting at - {socket.gethostname()} - {socket.gethostbyname(socket.gethostname())}")

counter = 0

s.bind((host, PORT))  # Bind to the port

'''
Your design should include the request queue, threading code for the thread pool,
and any synchronization needed to insert or remove requests from the queue and notify threads.
'''

logger.info("Server ready")
s.listen(5)  # Now wait for client connection
while True:

    counter += 1

    # Establish connection with client
    c, addr = s.accept() 
    logger.info(f"Connection from {addr} has been established. {counter}")

    # process client request
    request_q.put(c)
    logger.debug(f"Added client request to queue")
