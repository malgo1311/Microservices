import unittest
import requests

host = "0.0.0.0"
port = 8000

main_url = f"http://{host}:{port}"
post_url = f"{main_url}/orders"

# FUNCTION TO MAKE GET REQUEST
def get_request(url):
    response = requests.get(url, timeout=5)
    print(f"GET - {url} - {response.status_code} - {response.text}")
    return response.status_code

# FUNCTION TO MAKE POST REQUEST
def post_request(url, payload):
    response = requests.post(url, json=payload, timeout=5)
    print(f"POST - {response.status_code} - {response.text}")
    return response.status_code

class TestService(unittest.TestCase):

    import re

    # TEST GET REQUEST FOR STOCK LOOKUP
    def test_get_lookup_fn(self):

        print("\nTesting GET requests for STOCK LOOKUP\n")
        
        # Case 1: TEST CASE FOR CORRECT URL AND CORRECT STOCK NAME
        self.assertTrue( get_request(f"{main_url}/stocks/BoarCo") == 200, "Get lookup request : Failed case 1")

        # Case 2: TEST CASE FOR CORRECT URL AND INCORRECT STOCK NAME
        self.assertTrue( get_request(f"{main_url}/stocks/Ash") == 400, "Get lookup request : Failed case 2")

        # Case 3: TEST CASE FOR INCORRECT URL
        self.assertTrue( get_request(f"{main_url}/stcks/BoarCo") == 404, "Get lookup request : Failed case 3")

        print("\nAll GET requests ran successfully which expected responses for STOCK LOOKUP")

    # TEST GET REQUEST FOR ORDER QUERY
    def test_get_query_fn(self):

        print("\nTesting GET requests for ORDER QUERY\n")
        
        # Case 1: TEST CASE FOR CORRECT URL AND CORRECT ORDER NUMBER
        self.assertTrue( get_request(f"{main_url}/orders/1") == 200, "Get query request : Failed case 1")

        # Case 2: TEST CASE FOR CORRECT URL AND INCORRECT ORDER NUMBER
        self.assertTrue( get_request(f"{main_url}/orders/1ac") == 404, "Get query request : Failed case 2")

        # Case 3: TEST CASE FOR INCORRECT URL
        self.assertTrue( get_request(f"{main_url}/ordrs/2") == 404, "Get query request : Failed case 3")

        print("\nAll GET requests ran successfully which expected responses for ORDER QUERY")

    # TEST GET REQUEST FOR ORDER LEADER
    def test_get_order_leader_fn(self):

        print("\nTesting GET requests for ORDER LEADER\n")
        
        # Case 1: TEST CASE FOR CORRECT URL AND CORRECT ORDER NUMBER
        self.assertTrue( get_request(f"{main_url}/get_order_leader") == 200, "Get order leader request : Failed case 1")

        # Case 2: TEST CASE FOR INCORRECT URL
        self.assertTrue( get_request(f"{main_url}/get_order_lader") == 404, "Get order leader request : Failed case 2")

        print("\nAll GET requests ran successfully which expected responses for ORDER LEADER")


    # TEST GET REQUEST FOR CACHE INVALIDATION
    def test_get_cache_invalid_fn(self):

        print("\nTesting GET requests for CACHE INVALIDATION\n")
        
        # Case 1: TEST CASE FOR CORRECT URL AND CORRECT ORDER NUMBER
        self.assertTrue( get_request(f"{main_url}/cache_invalid/FishC") == 200, "Get cache_invalid request : Failed case 1")

        # Case 2: TEST CASE FOR INCORRECT URL
        self.assertTrue( get_request(f"{main_url}/cache_invald/FishCo") == 404, "Get cache_invalid request : Failed case 2")

        print("\nAll GET requests ran successfully which expected responses for CACHE INVALIDATION")


    # TEST POST REQUEST
    def test_post_fn(self):

        print("\n\nTesting POST requests\n")
        
        # Case 1: TEST CASE FOR CORRECT URL AND CORRECT TRADE INFORMATION
        payload = {"name": "GameStart",
                    "quantity": 10,
                    "type": "sell"}
        self.assertTrue( post_request(post_url, payload) == 200, "Post request : Failed case 1")

        # Case 2: TEST CASE FOR CORRECT URL AND INCORRECT STOCK NAME IN TRADE INFORMATION
        payload = {"name": "Hey",
                    "quantity": 10,
                    "type": "buy"}
        self.assertTrue( post_request(post_url, payload) == 400, "Post request : Failed case 2")

        # Case 3: TEST CASE FOR CORRECT URL AND NEGATIVE QUANTITY IN TRADE INFORMATION
        payload = {"name": "MenhirCo",
                    "quantity": -10,
                    "type": "buy"}
        self.assertTrue( post_request(post_url, payload) == 400, "Post request : Failed case 3")

        # Case 4: TEST CASE FOR CORRECT URL AND UNKNOWN TRADE TYPE IN TRADE INFORMATION
        payload = {"name": "MenhirCo",
                    "quantity": 10,
                    "type": "negotiate"}
        self.assertTrue( post_request(post_url, payload) == 400, "Post request : Failed case 4")

        # Case 5: TEST CASE FOR INCORRECT URL
        payload = {"name": "MenhirCo",
                    "quantity": 10,
                    "type": "negotiate"}
        self.assertTrue( post_request(f"{main_url}/ordrs", payload) == 404, "Post request : Failed case 5")

        # Case 6: TEST CASE WHEN THE QUANTITY TO BUY IS VERY HIGH
        payload = {"name": "GameStart",
                    "quantity": 9999999999999999,
                    "type": "buy"}
        self.assertTrue( post_request(post_url, payload) == 500, "Post request : Failed case 6")

        print("\nAll POST requests ran successfully with expected responses")


if __name__ == "__main__":
    unittest.main()