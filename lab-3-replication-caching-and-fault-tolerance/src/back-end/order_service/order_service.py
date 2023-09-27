import sys
import json
import threading
import Pyro5.api
import Pyro5.errors
import pandas as pd

# IMPORTING READ-WRITE LOCK
import rw_lock

import setup
logger = setup.logger

import ft_helper

# ADDED THESE LINES BECAUSE EDLAB WAS THROWING THREADING ERROR
# YOU CAN COMMENT THESE TWO LINES IF RUNNING ON LOCAL
# import os
# os.environ['OPENBLAS_NUM_THREADS'] = '1'

@Pyro5.api.expose
class Order(object):
    '''
    CREATING PYRO RPC TO EXPOSE ORDER METHODS
    1) TRADE METHOD
        THIS FUNCTION IS CALLED BY THE FRONT-END
        IT CALLS THE 'EXECUTE TRADE METHOD' OF CATALOG SERVICE
    2) RECORD TRANSACTION (__record_txn)
        THIS FUNCTION INCREMENTS THE TRANSACTION NUMBER AND WRITE
        IT TO THE ORDER LOG
    '''

    # INITIALIZING TRANSACTION NUMBER TO 0
    TXN_NUM = setup.initial_txn_num
    logger.info(f"TXN_NUM is initialized as {TXN_NUM}")

    # LOADING ORDER LOG FROM PERSISTENT LOCATION AT SYSTEM START TIME
    logger.info("Loading order log")
    ORDER_LOG = pd.read_csv(setup.txn_file_path)
    # logger.info(f"ORDER_LOG {ORDER_LOG}")

    # SYNC WITH LEADER
    TXN_NUM, ORDER_LOG = ft_helper.sync_at_start(TXN_NUM, ORDER_LOG)
    # logger.info(f"ORDER_LOG {ORDER_LOG}")

    # INITIALIZING READ-WRITE LOCK
    RW_LOCK = rw_lock.RWLock()

    # INITIALIZING LEADER FLAG
    # REPRESENTS WHETHER THIS REPLICA IS LEADER OR NOT
    LEADER_FLAG = False

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
            # GENERATING TXN NUMBER WITH THREAD WRITE LOCK
            with Order.RW_LOCK.write_access:

                logger.debug(f"Write lock - acquired")

                Order.TXN_NUM += 1
                curr_txn_num = Order.TXN_NUM

                # APPENDING TRADE DETAILS TO THE PERSISTENT LOCATION
                temp_df = pd.DataFrame([[curr_txn_num, stock_name, trade_type, abs(change_in_quantity)]])
                temp_df.to_csv(setup.txn_file_path, mode='a', index=False, header=False)
                
                # logger.debug(f"temp_df - {temp_df}")
                # APPENDING TRADE DETAILS TO IN-MEMORY DATA
                temp_df = pd.DataFrame([[curr_txn_num, stock_name, trade_type, abs(change_in_quantity)]],
                                        columns=setup.orderlog_col_names)
                Order.ORDER_LOG = pd.concat([Order.ORDER_LOG, temp_df], ignore_index = True)
                temp_df = {"transaction_number": curr_txn_num,
                            "stock_name": stock_name,
                            "order_type": trade_type,
                            "trade_quantity": abs(change_in_quantity)}
                # Order.ORDER_LOG = Order.ORDER_LOG.append(temp_df, ignore_index = True)

                temp_df = {"transaction_number": curr_txn_num,
                            "stock_name": stock_name,
                            "order_type": trade_type,
                            "trade_quantity": abs(change_in_quantity)}
                
                # logger.debug(f"ORDER_LOG - {Order.ORDER_LOG}")

            logger.debug(f"Write lock - released")

            # GENERATING RESPONSE
            # if code == 200:
            response = {"data": {
                                "transaction_number": int(curr_txn_num)
                            }
                        }

            # IF THIS PROCESS IS LEADER THEN PROPAGATING TRADE INFO TO ALL REPLICAS
            if Order.LEADER_FLAG:

                # CHECKING WITH THE ID NUMBER IS DESCENDING ORDER
                for ns_port_temp in sorted(setup.replicated_order_ns, reverse=True):
                    
                    # DO NOT PROPAGATE DATA TO SELF
                    if ns_port_temp == setup.NS_PORT:
                        continue

                    # CALLING FUNCTION TO UPDATE CURRENT TRADE  ORDER SERVICE
                    logger.info(f"Notifying {ns_port_temp} replica of order leader - txn_num {response['data']['transaction_number']}")
                    with Pyro5.api.Proxy(f"PYRONAME:{setup.order_service_name}@{setup.order_ns_host}:{ns_port_temp}") as backend_order:
                    
                        try:
                            response_temp = backend_order.record_leader_trades(temp_df)
                        
                       # IF THE NAMESERVER DOESN'T RESPOND THEN CHOOSE A NEW LEADER
                        except Pyro5.errors.NamingError:
                            response_temp = f"Cannot reach {ns_port_temp} replica"
                            logger.info(f"{response_temp}")
                            
                        # IF THE SERVICE DOESN'T RESPOND THEN CHOOSE A NEW LEADER
                        except Pyro5.errors.CommunicationError:
                            response_temp = f"Cannot reach {ns_port_temp} replica"
                            logger.info(f"{response_temp}")

                        # SHOW TRACEBACK INCASE OF LOGICAL ERROR
                        except Exception:
                            response_temp = 'Internal Server Error. Check pyro traceback. From Back-end Order __record_txn fn'
                            logger.error("Pyro traceback:")
                            logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")

                    logger.info(f"Response from replica - {response_temp}")

            return 200, response

        else:
            return code, message

    
    # FUNCTION TO QUERY THE ORDER NUMBER IN ORDER LOG
    def query(self, order_number):

        if not isinstance(order_number, int):
            response = f"Bad request. {order_number} is not an integer"
            logger.info(response)
            code = 400
            return code, response

        # logger.debug(f"{(Order.ORDER_LOG['transaction_number'])}")
        # logger.debug(f"All orders - {list(Order.ORDER_LOG['transaction_number'])}")

        # ACQUIRING READ LOCK
        with Order.RW_LOCK.read_access:

            logger.debug(f"Read lock - acquired")

            # CHECK IF STOCK NAME IS VALID
            if order_number in list(Order.ORDER_LOG["transaction_number"]):
                logger.info(f"{order_number} present in order log")

                # GENERATE RESPONSE
                response = {"data": {
                                    "number": order_number,
                                    "name": Order.ORDER_LOG[Order.ORDER_LOG['transaction_number']==order_number]['stock_name'].item(),
                                    "type": Order.ORDER_LOG[Order.ORDER_LOG['transaction_number']==order_number]['order_type'].item(),
                                    "quantity": Order.ORDER_LOG[Order.ORDER_LOG['transaction_number']==order_number]['trade_quantity'].item()
                                }
                            }
                code = 200

            # RETURN ERROR IF STOCK NAME IS INVALID
            else:
                response = f"Bad request. {order_number} order not found in ORDER LOG"
                logger.info(response)
                code = 400

        logger.debug(f"Read lock - released")

        return code, response


    # FUNCTION FOR HEALTH CHECK
    # def health_check(self):
    #     logger.info(f"Checking health of {setup.NS_PORT} order service")
    #     return "OK"


    # FUNCTION FOR GETTING INFO ABOUT LEADER
    def leader_notification(self, leader_port):

        if leader_port == setup.NS_PORT:
            Order.LEADER_FLAG = True
            logger.info(f"This process is the leader of the replicated order pool - Flag is {Order.LEADER_FLAG}")

        else:
            Order.LEADER_FLAG = False
            logger.info(f"This process is a replica - Flag is {Order.LEADER_FLAG}")

        return "OK"


    # FUNCTION TO RECORD TRADES FROM LEADER
    def record_leader_trades(self, data):

        # RETURN ERROR IF DATA IS NOT DICTIONARY
        if not isinstance(data, dict):
            response = f"Bad request. {data} is not a dictionary. Cannot writing trade data from leader"
            logger.error(response)
            return "ERROR"

        # RETURN ERROR IF DATA DOES NOT INCLUDE ANY OF THE KEYS
        for key in ['transaction_number', 'stock_name', 'order_type', 'trade_quantity']:
            if key not in data.keys():
                response = f"Bad request. {key} key not present in input. Cannot writing trade data from leader"
                logger.error(response)
                return "ERROR"

        logger.debug(f"Writing trade data from leader - {data}")
        
        # DONT ADD TRADE DATA TO DB IF IT IS ALREADY UPDATED
        if data['transaction_number'] in list(Order.ORDER_LOG['transaction_number']):
            logger.info(f"No update required, since data is already captured")

        else:

            # THREAD WRITE LOCK TO UPDATE PERSISTENT AND IN-MEMORY DB
            with Order.RW_LOCK.write_access:

                logger.debug(f"Write lock - acquired")

                # APPENDING TRADE DETAILS TO THE PERSISTENT LOCATION
                temp_df = pd.DataFrame([[data['transaction_number'], data['stock_name'],
                                        data['order_type'], data['trade_quantity']]])
                temp_df.to_csv(setup.txn_file_path, mode='a', index=False, header=False)
                
                # APPENDING TRADE DETAILS TO IN-MEMORY DATA
                # Order.ORDER_LOG = Order.ORDER_LOG.append(data, ignore_index = True)
                temp_df = pd.DataFrame([[data['transaction_number'], data['stock_name'],
                                        data['order_type'], data['trade_quantity']]],
                                        columns=setup.orderlog_col_names)
                Order.ORDER_LOG = pd.concat([Order.ORDER_LOG, temp_df], ignore_index = True)

                # UPDATING TRANSACTION NUMBER
                # IF CONDITION CHECKS IF A LOWER TRANSACTION NUMBER COMES LATER TO THE REPLICA
                Order.TXN_NUM = data['transaction_number'] if (Order.TXN_NUM < data['transaction_number']) else Order.TXN_NUM

                # logger.debug(f"ORDER_LOG - {Order.ORDER_LOG}")

            logger.debug(f"Write lock - released")
            logger.info(f"TXN_NUM is - {Order.TXN_NUM}")

        return "OK"


    # GET ORDER LOG DIFF WRT TO REPLICA FOR SYNCING AT START-TIME
    def get_order_log_diff(self, rep_txn_num):

        logger.debug(f"Reading order log for sending diff. Replica txn_num - {rep_txn_num}, leader txn_num - {Order.TXN_NUM}")

        diff = None

        # THREAD WRITE LOCK TO GET THE LOG DIFF
        # SO THAT NOTHING IS WRITTEN IN ANY OTHER THREAD
        with Order.RW_LOCK.write_access:
            logger.debug(f"Write lock - acquired")

            # STORE LOG DIFF
            if Order.TXN_NUM > rep_txn_num:
                diff = Order.ORDER_LOG[Order.ORDER_LOG['transaction_number']>rep_txn_num]
                logger.debug(f"ORDER_LOG diff - {diff}")

            # RETURN ABORT IF REPLICA IS AHEAD OF LEADER
            elif Order.TXN_NUM < rep_txn_num:
                logger.info(f"Replica ahead of leader. Aborting replica")
                return "ABORT"
            
            # DO NOTHING IS REPLICA AND LEADER ARE SAME
            else:
                logger.info(f"Same txn_num, no diff in order log")

        logger.debug(f"Write lock - released")

        # SERIALIZE DIFF DATAFRAME FOR TRANSFER OVER CONNECTION
        return diff.to_dict() if isinstance(diff, pd.DataFrame) else diff

# CONFIG FOR THREADED PYRO DAEMON
Pyro5.config.SERVERTYPE = "thread"
Pyro5.config.THREADPOOL_SIZE_MIN = 4
Pyro5.config.THREADPOOL_SIZE = 40

# CONFIG FOR ERROR ANALYSIS
Pyro5.config.DETAILED_TRACEBACK = True
Pyro5.config.LOGLEVEL = True
# Pyro5.config.LOGFILE = "order_pyro5.log"

# Pyro5.config.NS_HOST - localhost 
Pyro5.config.NS_PORT = setup.NS_PORT
Pyro5.config.NS_BCPORT = setup.NS_PORT+1 

# STARTING PYRO5 DAEMON REQUEST LOOP
daemon = Pyro5.server.Daemon(host=setup.daemon_host)            # MAKE A PYRO DAEMON
ns = Pyro5.api.locate_ns()                                      # FIND THE NAME SERVER
uri = daemon.register(Order)                                    # REGISTER CATALOG AS A PYRO OBJECT
ns.register("backend.order", uri)                               # REGISTER THE OBJECT WITH A NAME IN THE NAME SERVER

# # DISPLAYING PYRO DAEMON CONFIG
# for k, v in (Pyro5.config.as_dict()).items():
#     logger.debug(f"{k} - {v}")

# STARTING ORDER SERVICE
logger.info("Order service ready")
daemon.requestLoop()                    # START THE EVENT LOOP OF THE SERVER TO WAIT FOR CALLS