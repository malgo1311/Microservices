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

    # INITIALIZING SOME RANDOM AND CORRECT STOCK NAMES AND TRADE TYPES FOR TESTING
    stock_names = ["HelloWorld", "FishCo", "BoarCo", "MenhirCo"]
    trade_type = ["buy", "sell", "throw"]
    
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
                response = session.get(url, timeout=5)
            except Exception as err: 
                logger.error(str(err))
                continue
            end = time.time()       # TO CALCULATE LATENCY

            # EXTRACTING JSON OBJECT FROM THE RESPONSE
            json_response = json.loads(response.text)
            logger.info(f"Time {end-start:.10f} sec ; GET response for {stock_name} - {json_response}")

            logger.info(f"GET equest complete - {counter}")

            # SEND POST REQUEST ONLY IF LOOKUP RESPONSE IS SUCCESSFUL
            if response.status_code == 200:

                # PERFORMING POST REQUEST ON THE SAME STOCK WITH RANDOM PROBABILITY
                # ALSO CHECKING IF THE STOCK QUANTITY IS >0 FOR TRADING
                if random.uniform(0, 1) < setup.POST_probability and json_response["data"]["quantity"] > 0:

                    # CREATING TRADING JSON OBJECT FOR POST REQUEST
                    payload = {
                        "name": stock_name,
                        "quantity": random.randint(-10, 50),
                        "type": random.choice(trade_type)
                    }
                    logger.info(f"")
                    logger.info(f"Sending POST request to server - {stock_name} {payload}")
                    start = time.time()     # TO CALCULATE LATENCY
                    try:  
                        # SENDING POST REQUEST OVER SESSION
                        response = session.post(post_url, json=payload, timeout=5)
                    except Exception as err: 
                        logger.error(str(err))
                        continue
                    end = time.time()       # TO CALCULATE LATENCY

                    # EXTRACTING JSON OBJECT FROM THE RESPONSE
                    json_response = json.loads(response.text)
                    logger.info(f"Time {end-start:.10f} sec ; POST response for {stock_name} - {json_response}")

                    logger.info(f"POST equest complete - {counter}")

            if counter >= 10: break

    # SESSION ENDS AFTER 'WITH' STATEMENT EXITS
    logger.info(f"Session closed")

    