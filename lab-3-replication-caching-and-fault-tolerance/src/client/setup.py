import logging
import pandas as pd

# CONFIGURING LOGGER
# logging.basicConfig(format='%(asctime)s : %(filename)s : %(threadName)s : %(message)s')
logging.basicConfig(format='%(threadName)s : %(message)s ')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# ADD THE CORRECT HOST ADDRESS AND PORT NUMBER OF THE SERVER
host = "0.0.0.0" #"localhost"
port = 8000

# PROBABILITY FOR SENDING POST SEQUEST
POST_probability = 1      # set a value between [0,1]

MAX_REQ_BY_CLIENT = 200