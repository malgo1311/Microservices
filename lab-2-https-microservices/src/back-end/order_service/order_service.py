import json
import threading
import Pyro5.api
import Pyro5.errors
import pandas as pd

import setup
logger = setup.logger

# ADDED THESE LINES BECAUSE EDLAB WAS THROWING THREADING ERROR
# YOU CAN COMMENT THESE TWO LINES IF RUNNING ON LOCAL
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'

class Order(object):
    '''
    CREATING PYRO RPC TO EXPOSE ORDER METHODS
    1) TRADE METHOD
        THIS FUNCTION IS CALLED BY THE FRONT-END
        IT CALLS THE 'EXECUTE TRADE METHOD' OF CATALOG SERVICE
    2) RECORD TRANSACTION (__record_txn_v2)
        THIS FUNCTION INCREMENTS THE TRANSACTION NUMBER AND WRITE
        IT TO THE ORDER LOG
    '''

    # INITIALIZING TRANSACTION NUMBER TO 0
    TXN_NUM = setup.initial_txn_num
    logger.info(f"TXN_NUM is initialized as {TXN_NUM}")

    # INITIALIZING WRITE LOCK FOR ORDER LOG
    TXN_NUM_WLOCK = threading.Lock()


    @Pyro5.api.expose
    def trade(self, data):

        logger.info(f"Received trade request - {data} {type(data)}")

        try:
            stock_name = str(data["name"])
            trade_quantity = int(data["quantity"])
            trade_type = str(data["type"])

        except Exception as e:
            message = "POST data not in correct format. " + str(e)
            logger.info(f"{message}")
            return 400, message

        # CHECK IF TRADE QUANTITY IS VALID
        if trade_quantity <= 0:
            message = f"Invalid quantity {trade_quantity}"
            logger.info(f"{message}")
            return 400, message

        # CHECK TRADE TYPE
        elif trade_type not in ["buy", "sell"]:
            message = f"Unknow trade type - {trade_type}"
            logger.info(f"{message}")
            return 400, message
        
        logger.info(f"Calling lookup service - {stock_name}")
        with Pyro5.api.Proxy(f"PYRONAME:{setup.catalog_service_name}@{setup.catalog_ns_host}:{setup.catalog_ns_port}") as backend_catalog:
            try:
                code, lookup_response = backend_catalog.lookup(stock_name)
            except Exception:
                code = 500
                lookup_response = "Internal Server Error. Check pyro traceback. From Back-end lookup"
                logger.info("Pyro traceback:")
                logger.info(f"{''.join(Pyro5.errors.get_pyro_traceback())}")
        logger.info(f"Received lookup response  - {code} {lookup_response}")

        # PROCEED WITH ORDER IF LOOKUP RESPONSE IS SUCCESSFUL
        if code == 200:
            lookup_response = lookup_response["data"]
            logger.info(f"{stock_name} present in db")

            if trade_type == "sell":
                change_in_quantity = 1 * trade_quantity
                trade_code = 200

            elif trade_type == "buy":
                if lookup_response["quantity"] >= trade_quantity:
                    change_in_quantity = -1 * trade_quantity
                    trade_code = 200
                    
                else:
                    message = f"Insufficient volume for {stock_name} stock"
                    logger.info(f"{message}")
                    trade_code = 500
                    
                    return trade_code, message

            # IF TRADE IS SUCCESSFUL THEN ADDING DETAILS TO THE ORDER LOG
            if trade_code == 200:
                trade_code, response = self.__record_txn(stock_name, change_in_quantity, trade_type)
                logger.info(f"Executing - trade_code {trade_code} {type(trade_code)} - response {response} {type(response)}")
                logger.info(f"Executing {trade_type} trade for {stock_name} with {change_in_quantity} quantity")
            else:
                trade_code = 500
                response = "Internal server error. Check PyRO trade method in order service"
            
            return trade_code, response

        # NO TRADE IF LOOKUP RESPONSE IS UNSUCCESSFUL
        else:
            logger.info(f"{code} - {lookup_response}")
            return code, lookup_response

    # FUNCTION TO EXECUTE AND RECORD TRANSACTION
    def __record_txn(self, stock_name, change_in_quantity, trade_type):

        # CALLING CATALOG TO UPDATE DB
        logger.info(f"Calling update service - {stock_name}")
        with Pyro5.api.Proxy(f"PYRONAME:{setup.catalog_service_name}@{setup.catalog_ns_host}:{setup.catalog_ns_port}") as backend_catalog:
            try:
                code, message = backend_catalog.update(stock_name, change_in_quantity)
            except Exception:
                code = 500
                message = "Internal Server Error. Check pyro traceback. From Back-end Update"
                logger.info("Pyro traceback:")
                logger.info(f"{''.join(Pyro5.errors.get_pyro_traceback())}")
                return code, message
        logger.info(f"Received update response - {stock_name}")

        if code == 200:
            # GENERATING TXN NUMBER WITH THREAD LOCK
            with Order.TXN_NUM_WLOCK:
                Order.TXN_NUM += 1
                curr_txn_num = Order.TXN_NUM

                df = pd.DataFrame([[curr_txn_num, stock_name, trade_type, abs(change_in_quantity)]])

                # APPENDING TRADE DETAILS TO THE PERSISTENT LOCATION
                df.to_csv(setup.txn_file_path, mode='a', index=False, header=False)

            # GENERATING RESPONSE
            # if code == 200:
            response = {"data": {
                                "transaction_number": int(curr_txn_num)
                            }
                        }

            return 200, response

        else:
            return code, message
    

# STARTING PYRO5 DAEMON REQUEST LOOP
daemon = Pyro5.server.Daemon(host=setup.daemon_host)            # MAKE A PYRO DAEMON
ns = Pyro5.api.locate_ns()                                      # FIND THE NAME SERVER
uri = daemon.register(Order)                                    # REGISTER CATALOG AS A PYRO OBJECT
ns.register("backend.order", uri)                               # REGISTER THE OBJECT WITH A NAME IN THE NAME SERVER

# CONFIG FOR THREADED PYRO DAEMON
Pyro5.config.SERVERTYPE = "thread"
Pyro5.config.THREADPOOL_SIZE_MIN = 4
Pyro5.config.THREADPOOL_SIZE = 40

# CONFIG FOR ERROR ANALYSIS
Pyro5.config.DETAILED_TRACEBACK = True
Pyro5.config.LOGLEVEL = True
# Pyro5.config.LOGFILE = "order_pyro5.log"

# DISPLAYING PYRO DAEMON CONFIG
# for k, v in (Pyro5.config.as_dict()).items():
#     logger.debug(f"{k} - {v}")

# STARTING ORDER SERVICE
logger.info("Order service ready")
daemon.requestLoop()                    # START THE EVENT LOOP OF THE SERVER TO WAIT FOR CALLS
