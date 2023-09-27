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

# CHECKING FOR ENV VARIABLE TO SEE IS SYSTEM IS RUNNING ON DOCKER OR NOT
USING_DOCKER = os.getenv("USING_DOCKER", False)
if isinstance(USING_DOCKER, str): USING_DOCKER = eval(USING_DOCKER)
logger.info(f"USING_DOCKER is set as {USING_DOCKER} {type(USING_DOCKER)}")

if not USING_DOCKER:
    # ENTER NAME SERVER HOSTNAME FOR PYRO OBJECTS
    # FOR CATALOG SERVICE
    catalog_ns_host = "0.0.0.0" #"172.22.0.4" #"0.0.0.0"

    # FOR ORDER SERVICE
    order_ns_host = "0.0.0.0"

else:
    # ENTER NAME SERVER HOSTNAME FOR PYRO OBJECTS
    # FOR CATALOG SERVICE
    catalog_ns_host = "catalog" #"172.22.0.4" #"0.0.0.0"

    # FOR ORDER SERVICE
    order_ns_host = "order"

# ENTER PYRO SERVICE NAME AND PORT NUMBER OF PYRO NAME SERVERs
# FOR CATALOG SERVICE
catalog_service_name = "backend.catalog"
catalog_ns_port = "9090" #"8001"

# FOR ORDER SERVICE
order_service_name = "backend.order"
order_ns_port = "9090"
