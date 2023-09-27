#!/usr/bin/env python3

import json
import time
import random
import requests

import setup
logger = setup.logger

# SPECIFYING HTTP VERSION FOR CLIENT-SERVER COMMUNICATION
from http.client import HTTPConnection
HTTPConnection._http_vsn_str = 'HTTP/1.1'

if __name__ == "__main__":

    # SAVE ORDER DATA
    orders_list = []

    # INITIALIZING SOME RANDOM AND CORRECT STOCK NAMES AND TRADE TYPES FOR TESTING
    # stock_names = ["Hey", "FishCo", "BoarCo", "MenhirCo"]
    # trade_type = ["buy", "sell", "throw"]

    stock_names = ["FishCo", "BoarCo", "MenhirCo"]
    trade_type = ["buy", "sell"]
    
    # INITIALIZING REQUESTS COUNTER
    counter = 0

    # CONSTRUCTING SERVER SIDE FRONT-END URLS
    main_url = f"http://{setup.host}:{setup.port}"
    post_url = f"{main_url}/orders"

    # STARTING A SESSION
    with requests.Session() as session:

        logger.info(f"Created new session")
        
        while True:

            # RANDOMLY CHOSSING A STOCK FROM THE LIST
            stock_name = random.choice(stock_names)

            counter += 1
            logger.info(f"")

            # PERFORMING GET REQUEST ON RANDOMLY CHOSEN STOCK
            url = f"{main_url}/stocks/{stock_name}"

            logger.info(f"Sending GET request to server - {stock_name}")
            start = time.time()     # TO CALCULATE LATENCY
            try: 
                # SENDING GET REQUEST OVER SESSION
                response = session.get(url, timeout=10)
            except requests.exceptions.ConnectionError:
                logger.error(f"NewConnectionError - Aborting - Frontend is not up!")
                break
            except Exception as err: 
                logger.error(str(err))
                continue
            end = time.time()       # TO CALCULATE LATENCY

            # EXTRACTING JSON OBJECT FROM THE RESPONSE
            json_response = json.loads(response.text)
            logger.info(f"Lookup : Time {end-start:.10f} sec ; GET response for {stock_name} - {json_response}")

            logger.info(f"GET request complete - {counter}")

            # SEND POST REQUEST ONLY IF LOOKUP RESPONSE IS SUCCESSFUL
            if response.status_code == 200:

                # PERFORMING POST REQUEST ON THE SAME STOCK WITH RANDOM PROBABILITY
                # ALSO CHECKING IF THE STOCK QUANTITY IS >0 FOR TRADING
                if random.uniform(0, 1) < setup.POST_probability and json_response["data"]["quantity"] > 0:

                    # CREATING TRADING JSON OBJECT FOR POST REQUEST
                    payload = {
                        "name": stock_name,
                        "quantity": random.randint(-5, 50),
                        "type": random.choice(trade_type)
                    }
                    logger.info(f"")
                    logger.info(f"Sending POST request to server - {stock_name} {payload}")
                    start = time.time()     # TO CALCULATE LATENCY
                    try:  
                        # SENDING POST REQUEST OVER SESSION
                        response = session.post(post_url, json=payload, timeout=10)
                    except requests.exceptions.ConnectionError:
                        logger.error(f"NewConnectionError - Aborting - Frontend is not up!")
                        break
                    except Exception as err: 
                        logger.error(str(err))
                        continue
                    end = time.time()       # TO CALCULATE LATENCY

                    # EXTRACTING JSON OBJECT FROM THE RESPONSE
                    json_response = json.loads(response.text)
                    logger.info(f"Trade : Time {end-start:.10f} sec ; POST response for {stock_name} - {json_response}")

                    logger.info(f"POST request complete - {counter}")

                    # SAVE ORDERS IF RESPONSE IS SUCCESSFUL
                    if response.status_code == 200:
                        orders_list.append([json_response, payload])
                    
            if counter >= setup.MAX_REQ_BY_CLIENT: break

        logger.info(f"")
        # logger.info(f"orders_list - {orders_list}")
        executed_order_num = [orders_list[i][0]['data']['transaction_number'] for i in range(len(orders_list))]
        logger.info(f"Orders executed by this client - {executed_order_num}")
        logger.info(f"")

        # RETRIEVE ORDER INFO USING QUERY REQUEST
        for order in orders_list:
            txn_num = order[0]['data']['transaction_number']
            payload = order[1]

            # BUILDING URL FOR QUERY REQUEST
            query_url = f"{main_url}/orders/{txn_num}"
            
            logger.info(f"Sending GET request to server for order query - {txn_num}")
            start = time.time()     # TO CALCULATE LATENCY
            try: 
                # SENDING GET REQUEST OVER SESSION
                response = session.get(query_url, timeout=10)
            except requests.exceptions.ConnectionError:
                logger.error(f"NewConnectionError - Aborting - Frontend is not up!")
                break
            except Exception as err: 
                logger.error(str(err))
                continue
            end = time.time()       # TO CALCULATE LATENCY

            # EXTRACTING JSON OBJECT FROM THE RESPONSE
            json_response = json.loads(response.text)
            logger.info(f"Query : Time {end-start:.10f} sec ; GET response for query {txn_num} - {json_response}")

            if response.status_code == 200:
                json_response = json_response['data']
                check = 0
                for key in ["name", "quantity", "type"]:
                    if payload[key] == json_response[key]: check += 1

                if check == 3:
                    logger.info(f"Local and server order details match for {txn_num} order number")
                else:
                    logger.info(f"Local and server order details DOES NOT match for {txn_num} order number")
            
            else:
                logger.error(f"No response from server for {txn_num} order number")

            logger.info(f"")

    # SESSION ENDS AFTER 'WITH' STATEMENT EXITS
    logger.info(f"Session closed")

    