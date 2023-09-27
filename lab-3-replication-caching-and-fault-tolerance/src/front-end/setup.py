import os
import logging
import pandas as pd

# CONFIGURING LOGGER
# logging.basicConfig(format='%(asctime)s : %(filename)s : %(threadName)s : %(message)s')
logging.basicConfig(format='%(threadName)s : %(message)s ')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# INITIALIZE THE IP ADDRESS AND PORT NUMBER ON WHICH TO SERVE SERVER
host = "0.0.0.0"
port = 8000

# ENTER PYRO SERVICE NAME AND HOSTNAME + PORT NUMBER OF PYRO NAME SERVERs
# FOR CATALOG SERVICE
catalog_ns_host = "0.0.0.0"
catalog_service_name = "backend.catalog"
catalog_ns_port = 9096

# FOR ORDER SERVICE
order_ns_host = "0.0.0.0"
order_service_name = "backend.order"
replicated_order_ns = [9090, 9092, 9094]

# REDIS CONFIG
redis_host = "localhost"
redis_port = 6379
redis_ttl = 600 #time in seconds