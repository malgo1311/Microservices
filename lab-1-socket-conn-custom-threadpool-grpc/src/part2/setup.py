import logging
# HOST = 'localhost' # local host

HOST = 'elnux3.cs.umass.edu' # Edlab host name
PORT = 12126 # Port number 


MAX_WORKERS = 2 # maximum number of Worker Threads
MAX_CONCURRENT_RPC = 20 # maximum concurrent rpc allowed

# Dictionary to store the stock information
stocksDB = {"GameStart": {"price": 14.96,"volume":0 ,"limit": 100},
                "FishCo": {"price": 17.99, "volume":0 ,"limit": 45},
                "BoarCo": {"price": 78.99, "volume":0 ,"limit": 500},
                "MenhirCo": {"price": 59.99, "volume":0 ,"limit": 850}}

# Number of times the query has to be run
QUERYCOUNT = 100

logging.basicConfig(format='%(asctime)s %(filename)s %(threadName)s %(message)s ')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
