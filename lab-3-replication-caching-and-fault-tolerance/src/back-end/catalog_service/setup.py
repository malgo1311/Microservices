import os
import logging
import pandas as pd


# CONFIGURING LOGGER
# logging.basicConfig(format='%(asctime)s : %(filename)s : %(threadName)s : %(message)s')
logging.basicConfig(format='%(threadName)s : %(message)s ')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# HOST AND PORT OF FRONT END SERVICE FOR CACHE INVALIDATION
host_frontend = "0.0.0.0" #"localhost"
port_frontend = 8000

# GETTING NAMESERVER PORT FROM ENVIRONMENT
NS_PORT = int(os.getenv("NS_PORT"))

# DEFINING BASE DIRECTORY
# ASSUMING SCRIPTS WILL RUN FROM INSIDE SRC FOLDER
BASE_DATA_DIR = os.path.join(os.getcwd(), "back-end/catalog_service/data")

if not os.path.exists(BASE_DATA_DIR):
    os.makedirs(BASE_DATA_DIR)

# CREATE AND INITIALIZE STOCK DATABASE AT BACKEND SYSTEM START TIME
db_file_path = os.path.join(BASE_DATA_DIR, "stock_db.csv")

# SPECIFYING ORDER SERVICE DAEMON HOST
daemon_host = None

# CHECKING IS STOCK DB IS PRESENT
if os.path.isfile(db_file_path):
    logger.info("Existing Stock DB File Found.")

# IF NOT PRESENT, THEN CREATING STOCK DB
else:
    logger.info("Creating Stock DB File.")
    df = pd.DataFrame([["GameStart",9.99,700,0],
                        ["FishCo",17.99,500,0],
                        ["BoarCo",28.59,1000,0],
                        ["MenhirCo",38.69,1500,0],
                        ["HatShop",12.99,250,0],
                        ["ShoeCo",45.99,789,0],
                        ["ToyWorld",24.99,1200,0],
                        ["TechMart",899.99,150,0],
                        ["SportsHive",5.99,450,0],
                        ["BeautyBox",19.99,230,0]],
                        columns=["name", "price", "quantity", "trading_volume"])
    df.to_csv(db_file_path, sep=",", index=False)