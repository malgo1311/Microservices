import sys
import json
import requests
import pandas as pd

import Pyro5.api
import Pyro5.errors

import setup
logger = setup.logger

url = f"http://{setup.host_name}:{setup.host_port}/get_order_leader"

def sync_at_start(TXN_NUM, ORDER_LOG):

    logger.info(f"Order replica just started. Trying to sync")

    order_log_diff = sync_with_leader(TXN_NUM) #setup.initial_txn_num)

    # UPDATE ORDER LOG IF DIFF IS VALID
    if order_log_diff:

        order_log_diff = pd.DataFrame(order_log_diff)

        # GENERATING TXN NUMBER WITH THREAD WRITE LOCK
        # with Order.RW_LOCK.write_access:
        # logger.debug(f"Write lock - acquired")

        # UPDATING IN-MEMORY DB
        ORDER_LOG = pd.concat([ORDER_LOG, order_log_diff], ignore_index=True)

        # UPDATING PERSISTENT DB
        order_log_diff.to_csv(setup.txn_file_path, mode='a', index=False, header=False)

        # UPDATING TXN NUMB
        TXN_NUM = max(list(ORDER_LOG['transaction_number']))
        logger.info(f"Updated TXN_NUM is {TXN_NUM}")

    # logger.info(f"Sync done")

    return TXN_NUM, ORDER_LOG

def sync_with_leader(TXN_NUM):

    leader_ns_port = None
    ORDER_LOG_DIFF = None

    logger.info("Checking for leader at startup time")
    # GETTING LEADER DETAILS FORM FRONTEND
    try: 
        leader_ns_port = requests.get(url, timeout=5)
        leader_ns_port = (json.loads(leader_ns_port.text))["data"]["order_leader"]

    # DO NOTHING IF FRONTEND IS NOT UP
    except requests.exceptions.ConnectionError:
        logger.error(f"NewConnectionError - Aborting - Frontend is not up!")

    # EXIT AND ABORT IN CASE OF ERROR
    except Exception as err:
        logger.error(str(err))
        sys.exit()

    if leader_ns_port:
        logger.info(f"Leader found at startup time, syncing... {leader_ns_port} {type(leader_ns_port)}")
        ORDER_LOG_DIFF = get_order_diff_from_leader(TXN_NUM, leader_ns_port)
    else:
        logger.info("No leader found at startup time, no sync required")

    return ORDER_LOG_DIFF


# SETTING UP REPLICA WITH THE LEADER
def get_order_diff_from_leader(TXN_NUM, leader_ns_port):
    
    order_log_diff = None

    # GETTING LATEST TRANSACTION NUMBER FROM LEADER
    logger.info(f"Calling get_order_log_diff from {leader_ns_port} order leader")
    with Pyro5.api.Proxy(f"PYRONAME:{setup.order_service_name}@{setup.order_ns_host}:{leader_ns_port}") as backend_order:

        try:
            order_log_diff = backend_order.get_order_log_diff(TXN_NUM)

        # SHOW TRACEBACK INCASE OF LOGICAL ERROR
        except Exception:
            logger.error("Pyro traceback:")
            logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")
            logger.info("Aborting replica since it cannot sync with leader")
            sys.exit()

    # logger.debug(f"order_log_diff - {type(order_log_diff)} - {order_log_diff}")

    if order_log_diff == "ABORT":
        sys.exit()

    # # UPDATE ORDER LOG IF DIFF IS VALID
    # if order_log_diff:

    #     order_log_diff = pd.DataFrame(order_log_diff)

        # # UPDATING IN-MEMORY DB
        # ORDER_LOG = pd.concat([ORDER_LOG, order_log_diff], ignore_index=True)

        # # UPDATING PERSISTENT DB
        # order_log_diff.to_csv(txn_file_path, mode='a', index=False, header=False)

        # # UPDATING TXN NUMB
        # TXN_NUM = max(list(ORDER_LOG['tr']))
        # logger.info(f"Updated TXN_NUM is {TXN_NUM}")

    logger.info("Sync done")

    return order_log_diff

'''
# SETTING UP REPLICA WITH THE LEADER
def sync_with_leader(TXN_NUM, ORDER_LOG):
    if os.path.isfile(leader_config):
        logger.info("Leader found at startup time, syncing...")

        order_log_diff = None

        # INCASE LEADER FAILS, TRY LEADER ELECTION AND RESEND REQUEST THRICE
        max_try = 0
        while max_try < 3:

            # GET LEADER FROM LEADER CONFIG FILE
            with open(leader_config, "r") as fp:
                for line in fp:
                    leader_ns_port = line

            # GETTING LATEST TRANSACTION NUMBER FROM LEADER
            logger.info(f"Calling get_order_log_diff from {leader_ns_port} order leader")
            with Pyro5.api.Proxy(f"PYRONAME:{order_service_name}@{order_ns_host}:{leader_ns_port}") as backend_order:

                try:
                    order_log_diff = backend_order.get_order_log_diff(TXN_NUM)
                    break

                # INCASE NAMESERVER OF THE BACKEND SERVICE IS DOWN
                except Pyro5.errors.NamingError: #Pyro5.errors.CommunicationError:
                    logger.info(f"Leader {leader_ns_port} not responsing. Waiting and trying again...")
                    max_try += 1
                    time.sleep(2)

                # INCASE THE BACKEND SERVICE IS DOWN
                except Pyro5.errors.CommunicationError:
                    logger.info(f"Leader {leader_ns_port} not responsing. Waiting and trying again...")
                    max_try += 1
                    time.sleep(2)

                # SHOW TRACEBACK INCASE OF LOGICAL ERROR
                except Exception:
                    logger.error("Pyro traceback:")
                    logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")
                    logger.info("Aborting replica since it cannot sync with leader")
                    sys.exit()

        # logger.debug(f"order_log_diff - {type(order_log_diff)} - {order_log_diff}")

        if order_log_diff == "ABORT":
            sys.exit()

        # UPDATE ORDER LOG IF DIFF IS VALID
        if order_log_diff:

            order_log_diff = pd.DataFrame(order_log_diff)

            # UPDATING IN-MEMORY DB
            ORDER_LOG = pd.concat([ORDER_LOG, order_log_diff], ignore_index=True)

            # UPDATING PERSISTENT DB
            order_log_diff.to_csv(txn_file_path, mode='a', index=False, header=False)

            # UPDATING TXN NUMB
            top = ORDER_LOG.head(1)
            bottom = ORDER_LOG.tail(1)
            concatenated = pd.concat([top,bottom])
            TXN_NUM = int(bottom['transaction_number'].iloc[0])

            logger.info(f"Updated TXN_NUM is {TXN_NUM}")

        logger.info("Sync done")

    # NO LEADER CONFIGURED YET - 
    else:
        logger.info("No leader found at startup time, no sync required")

    return TXN_NUM, ORDER_LOG

'''