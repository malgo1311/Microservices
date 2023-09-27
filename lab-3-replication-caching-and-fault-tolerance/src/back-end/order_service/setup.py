import os
import sys
import json
import time
import logging
import pandas as pd

import Pyro5.api
import Pyro5.errors

# CONFIGURING LOGGER
# logging.basicConfig(format='%(asctime)s : %(filename)s : %(threadName)s : %(message)s')
logging.basicConfig(format='%(threadName)s : %(message)s ')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# GETTING NAMESERVER PORT FROM ENVIRONMENT
NS_PORT = int(os.getenv("NS_PORT"))

# DEFINING BASE DIRECTORY
# ASSUMING SCRIPTS WILL RUN FROM INSIDE SRC FOLDER
BASE_DATA_DIR = os.path.join(os.getcwd(), "back-end/order_service/data")

if not os.path.exists(BASE_DATA_DIR):
    os.makedirs(BASE_DATA_DIR)

# DEFINE ORDER LOG CSV FILE PATH AT BACKEND SYSTEM START TIME
txn_file_path = os.path.join(BASE_DATA_DIR, f"order_log_{NS_PORT}.csv")

# DEFINE FILE PATH FOR STORING LEADER CONFIG
leader_config = os.path.join(BASE_DATA_DIR, f"leader_config.txt")

# NS PORT NUMBER FOR ALL REPLICAS
replicated_order_ns = [9090, 9092, 9094]

# SPECIFYING ORDER SERVICE DAEMON HOST
daemon_host = None

# FRONTEND DETAILS
host_name = "0.0.0.0"
host_port = 8000

# ENTER PYRO SERVICE NAME AND HOSTNAME + PORT NUMBER OF PYRO NAME SERVERs
# FOR CATALOG SERVICE
catalog_service_name = "backend.catalog"
catalog_ns_host = "0.0.0.0"
catalog_ns_port = 9096            # NAME SERVER POT NUMBER

# FOR ORDER SERVICE
order_ns_host = "0.0.0.0"
order_service_name = "backend.order"

orderlog_col_names = ["transaction_number", "stock_name", "order_type", "trade_quantity"]
# CHECKING IF ORDER LOG IS PRESENT
if os.path.isfile(txn_file_path):
    logger.info("Existing Order Log File Found.")

    # CHECKING IF LOG DATA PRESENT AND SETTING INITIAL TRANSACTION NUMBER ACCORDINGLY
    df = pd.read_csv(txn_file_path)
    top = df.head(1)
    bottom = df.tail(1)
    concatenated = pd.concat([top,bottom])

    if concatenated.empty:
        initial_txn_num = 0
    else:
        try:
            initial_txn_num = int(bottom['transaction_number'].iloc[0])
        except:
            initial_txn_num = 0

# IF ORDER LOG NOT PRESENT, THEN CREATING FILE AND SETTING INITIAL TRANSACTION NUMBER TO 0
else:
    logger.info("Creating Order Log File.")

    initial_txn_num = 0

    df = pd.DataFrame(columns=orderlog_col_names)
    df.to_csv(txn_file_path, sep=",", index=False)


