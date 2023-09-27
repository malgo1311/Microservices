import Pyro5.api
import pandas as pd

# IMPORTING READ-WRITE LOCK
import rw_lock
import requests

import setup
logger = setup.logger

# ADDED THESE LINES BECAUSE EDLAB WAS THROWING THREADING ERROR
# YOU CAN COMMENT THESE TWO LINES IF RUNNING ON LOCAL
# import os
# os.environ['OPENBLAS_NUM_THREADS'] = '1'

@Pyro5.api.expose
class Catalog(object):
    '''
    CREATING PYRO RPC TO EXPOSE CATALOG METHODS
    1) LOOKUP METHOD
        THIS FUNCTION IS CALLED BY THE FRONT-END
    2) EXECUTE TRADE METHOD
        THIS FUNCTION IS CALLED BY THE ORDER SERVICE
    '''

    # LOADING DB FROM PERSISTENT LOCATION AT SYSTEM START TIME
    logger.info("Loading stock db")
    STOCK_DB = pd.read_csv(setup.db_file_path)

    # INITIALIZING READ-WRITE LOCK
    RW_LOCK = rw_lock.RWLock()

    # FUNCTION TO LOOKUP THE STOCK DB
    def lookup(self, stock_name):
        
        logger.info(f"Received lookup request for - {stock_name}")

        # ACQUIRING READ LOCK
        with Catalog.RW_LOCK.read_access:

            logger.debug(f"Read lock - acquired")

            # CHECK IF STOCK NAME IS VALID
            if stock_name in list(Catalog.STOCK_DB["name"]):
                logger.info(f"{stock_name} present in db")

                # GENERATE RESPONSE
                response = {"data": {
                                    "name": stock_name,
                                    "price": Catalog.STOCK_DB[Catalog.STOCK_DB['name']==stock_name]['price'].item(),
                                    "quantity": Catalog.STOCK_DB[Catalog.STOCK_DB['name']==stock_name]['quantity'].item()
                                }
                            }
                code = 200

            # RETURN ERROR IF STOCK NAME IS INVALID
            else:
                response = f"Bad request. {stock_name} stock not found in db"
                logger.info(response)
                code = 400

        logger.debug(f"Read lock - released")

        return code, response

    
    # FUNCTION TO UPDATE THE STOCK DB
    def update(self, stock_name, change_in_quantity):

        logger.info(f"Received update request for - {stock_name}")

        try:
            # ACQUIRING WRITE LOCK
            with Catalog.RW_LOCK.write_access:

                logger.debug(f"Write lock - acquired")

                # CHECKING IF STOCK NAME PRESENT IN DB
                if stock_name not in Catalog.STOCK_DB['name'].values:
                    return 400, "Stock name not found"
                
                # UPDATING THE QUANTITY IN IN-MEMORY DB
                Catalog.STOCK_DB.loc[Catalog.STOCK_DB.name == stock_name, 'quantity'] += change_in_quantity

                # UPDATING THE TRADING VOLUME IN IN-MEMORY DB
                Catalog.STOCK_DB.loc[Catalog.STOCK_DB.name == stock_name, 'trading_volume'] += abs(change_in_quantity)
                
                # UPDATING THE PERSISTENT STORAGE
                Catalog.STOCK_DB.to_csv(setup.db_file_path, sep=",", index = False)

            logger.debug(f"Write lock - released")

            logger.info(f"Updated {stock_name} quantity by {change_in_quantity} in db")

            logger.info("Making cache invalid")
            requests.get(f"http://{setup.host_frontend}:{setup.port_frontend}/cache_invalid/{stock_name}")
            logger.info("Cache invalidated")

            return 200, "success"

        except Exception as e:
            code = 500
            message = str(e)
            logger.info(f"Error in catalog update method - {message}")
            return code, message

# CONFIG FOR THREADED PYRO DAEMON
Pyro5.config.SERVERTYPE = "thread"
Pyro5.config.THREADPOOL_SIZE_MIN = 4
Pyro5.config.THREADPOOL_SIZE = 40

# CONFIG FOR ERROR ANALYSIS
Pyro5.config.DETAILED_TRACEBACK = True
Pyro5.config.LOGLEVEL = True
# Pyro5.config.LOGFILE = "catalog_pyro5.log"

# Pyro5.config.NS_HOST - localhost 
Pyro5.config.NS_PORT = setup.NS_PORT
Pyro5.config.NS_BCPORT = setup.NS_PORT+1 

# STARTING PYRO5 DAEMON REQUEST LOOP
daemon = Pyro5.server.Daemon(host=setup.daemon_host)            # MAKE A PYRO DAEMON
ns = Pyro5.api.locate_ns()                              # FIND THE NAME SERVER
uri = daemon.register(Catalog)                          # REGISTER CATALOG AS A PYRO OBJECT
ns.register("backend.catalog", uri)                     # REGISTER THE OBJECT WITH A NAME IN THE NAME SERVER

# DISPLAYING PYRO DAEMON CONFIG
# for k, v in (Pyro5.config.as_dict()).items():
#     logger.debug(f"{k} - {v}")

# STARTING CATALOG SERVICE
logger.info("Catalog service ready")
daemon.requestLoop()                   # START THE EVENT LOOP OF THE SERVER TO WAIT FOR CALLS
