import json
import threading
import logging
from setup import *

# creating lock for accessing the shared db
DB_Lock = threading.Lock()

# Lookup method
def Lookup(stockName, lock):

    # lock demonstration while accessing shared db
    # even though we feel that for read op it's not req
    with lock:

        # return stock price if stockName present in db
        if stockName in stocksDB.keys():

            value = stocksDB[stockName]["price"]
            return float(value)

        # return -1 if stockName not present in db
        else:
            return -1

        # return 0 if trading is suspended; not relevant for part1

# implementing thread safe queue
class Queue():

    # initializing queue and locks required for synchronization
    def __init__(self):
        self.q = []
        self.q_lock = threading.Condition(threading.Lock())

    # producer - blocks while appending the new client request
    # notifies one of the threads waiting on q_lock condition
    def put(self, item):
        
        with self.q_lock:
            self.q.append(item)
            self.q_lock.notify()
        
        return

    # consumer - waits on q_lock condition
    # until notified by the put function
    def get(self):

        with self.q_lock:
            self.q_lock.wait()
            item = self.q.pop(0)

        return item

# initializing FIFO client request queue
request_q = Queue()

# threadpool implementation
class Threadpool():

    def __init__(self, num_of_threads):
        
        # initializing and starting the threads
        for i in range(num_of_threads):
            t = threading.Thread(target=self.__process, daemon=True)
            t.start()

    def __process(self):

        exec_counter = 0
        logger.debug(f'Starting thread process')
        # while loop for threads to process next requests
        while True:

            # waiting on queue to get a client request
            logger.debug(f'Waiting to get request from request_q')
            c = request_q.get()
            logger.debug(f'Request received, processing request')

            # receive message from client
            message_from_client = c.recv(1024).decode()
            logger.debug(f'Message received from client')

            # deserialize the client message
            data = json.loads(message_from_client)
            logger.debug(f"Message deserialized")

            # get the method name to run
            methodName = data["methodName"]

            if methodName.lower() == "lookup":
                # run method and return value
                value = Lookup(data["arguments"]["stockName"], DB_Lock)
            else:
                value = f"methodName not found - {methodName}"

            # send lookup value back to client
            logger.debug(f'Sending response to client - {data["arguments"]["stockName"]}')
            c.send(str.encode(str(value)))

            # close the connection
            c.close()

            exec_counter += 1
            logger.debug(f"Request complete. Total requests processed - {exec_counter}")


            