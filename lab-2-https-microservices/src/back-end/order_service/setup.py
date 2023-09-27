import os
import logging
import pandas as pd


# CONFIGURING LOGGER
# logging.basicConfig(format='%(asctime)s : %(filename)s : %(threadName)s : %(message)s')
logging.basicConfig(format='%(threadName)s : %(message)s ')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# CHECKING FOR ENV VARIABLE TO SEE IS SYSTEM IS RUNNING ON DOCKER OR NOT
USING_DOCKER = os.getenv("USING_DOCKER", False)
if isinstance(USING_DOCKER, str): USING_DOCKER = eval(USING_DOCKER)
logger.info(f"USING_DOCKER is set as {USING_DOCKER} {type(USING_DOCKER)}")

if not USING_DOCKER:
    # CREAT ORDER LOG CSV FILE AT BACKEND SYSTEM START TIME
    txn_file_path = os.path.join(os.getcwd(), "src/back-end/order_service/data/order_log.csv")  

    # ENTER HOSTNAME FOR CATALOG SERVICE NAME SERVERs
    catalog_ns_host = "0.0.0.0"

    # SPECIFYING ORDER SERVICE DAEMON HOST
    daemon_host = None

else:
    # CREAT ORDER LOG CSV FILE AT BACKEND SYSTEM START TIME
    txn_file_path = "./data/order_log.csv"    

    # ENTER HOSTNAME FOR CATALOG SERVICE NAME SERVERs
    catalog_ns_host = "catalog" #"172.22.0.4" #"0.0.0.0"

    # SPECIFYING ORDER SERVICE DAEMON HOST
    daemon_host = "order"

# ENTER SERVICE NAME / IP ADDRESS AND PORT NUMBER FOR CATALOG SERVICE PYRO OBJECT
catalog_service_name = "backend.catalog"
catalog_ns_port = "9090" #"8001"            # NAME SERVER POT NUMBER


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

    df = pd.DataFrame(columns=["transaction_number", "stock_name", "order_type", "trade_quantity"])
    df.to_csv(txn_file_path, sep=",", index=False)