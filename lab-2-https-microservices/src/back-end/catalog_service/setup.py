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
    # CREATE AND INITIALIZE STOCK DATABASE AT BACKEND SYSTEM START TIME
    db_file_path = os.path.join(os.getcwd(), "src/back-end/catalog_service/data/stock_db.csv")

    # SPECIFYING ORDER SERVICE DAEMON HOST
    daemon_host = None

else:
    # CREATE AND INITIALIZE STOCK DATABASE AT BACKEND SYSTEM START TIME
    db_file_path = "./data/stock_db.csv"

    # SPECIFYING ORDER SERVICE DAEMON HOST
    daemon_host =  "catalog"

# CHECKING IS STOCK DB IS PRESENT
if os.path.isfile(db_file_path):
    logger.info("Existing Stock DB File Found.")

# IF NOT PRESENT, THEN CREATING STOCK DB
else:
    logger.info("Creating Stock DB File.")
    df = pd.DataFrame([["GameStart",9.99,100,0],
                        ["FishCo",17.99,500,0],
                        ["BoarCo",28.59,1000,0],
                        ["MenhirCo",38.69,1500,0]],
                        columns=["name", "price", "quantity", "trading_volume"])
    df.to_csv(db_file_path, sep=",", index=False)