#!/usr/bin/env python3

############################################################################

# PLEASE CHECK FRONTEND LOGS AFTER RUNNING THIS SCRIPT FOR CACHE VERIFICATION

############################################################################

import json
import time
import random
import requests

host = "0.0.0.0"
port = 8000

if __name__ == "__main__":

    # CHOSSING A STOCK
    stock_name = "FishCo"

    # CONSTRUCTING SERVER SIDE FRONT-END URLS
    main_url = f"http://{host}:{port}"
    post_url = f"{main_url}/orders"
    get_url = f"{main_url}/stocks/{stock_name}"

    # CREATING TRADING JSON OBJECT FOR POST REQUEST
    payload = {
        "name": stock_name,
        "quantity": 10,
        "type": "sell"
    }

    # STARTING A SESSION
    with requests.Session() as session:

        print(f"Created new session")

        print(f"")
        print(f"Sending GET request to server - {stock_name}")
        response = session.get(get_url, timeout=10)
        json_response = json.loads(response.text)
        print(f"Lookup : GET response for {stock_name} - {json_response}")
        print(f"GET request complete")

        # PERFORMING REQUEST AGAIN TO CHECK FOR CACHING
        print(f"")
        print(f"Sending GET request to server - {stock_name}")
        response = session.get(get_url, timeout=10)
        json_response = json.loads(response.text)
        print(f"Lookup : GET response for {stock_name} - {json_response}")
        print(f"GET request complete")

        
        # SEND POST REQUEST ONLY IF LOOKUP RESPONSE IS SUCCESSFUL
        if response.status_code == 200:

            print(f"")
            print(f"Sending POST request to server - {stock_name} {payload}")
            response = session.post(post_url, json=payload, timeout=10)
            # EXTRACTING JSON OBJECT FROM THE RESPONSE
            json_response = json.loads(response.text)
            print(f"Trade : POST response for {stock_name} - {json_response}")
            print(f"POST request complete")

        # PERFORMING GET REQUEST
        url = f"{main_url}/stocks/{stock_name}"

        print(f"")
        print(f"Sending GET request to server - {stock_name}")
        response = session.get(get_url, timeout=10)
        json_response = json.loads(response.text)
        print(f"Lookup : GET response for {stock_name} - {json_response}")
        print(f"GET request complete")

        # PERFORMING REQUEST AGAIN TO CHECK FOR CACHING
        print(f"")
        print(f"Sending GET request to server - {stock_name}")
        response = session.get(get_url, timeout=10)
        json_response = json.loads(response.text)
        print(f"Lookup : GET response for {stock_name} - {json_response}")
        print(f"GET request complete")
            
        
    # SESSION ENDS AFTER 'WITH' STATEMENT EXITS
    print(f"Session closed")

    