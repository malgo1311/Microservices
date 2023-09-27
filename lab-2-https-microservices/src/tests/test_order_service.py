import unittest
import requests
import Pyro5.api
import Pyro5.errors

order_service_name = "backend.order"
order_ns_host = "0.0.0.0"
order_ns_port = "9090"

# FUNCTION TO CALL ORDER TRADE SERVICE
def call_order_trade_service(data):

    with Pyro5.api.Proxy(f"PYRONAME:{order_service_name}@{order_ns_host}:{order_ns_port}") as backend_order:
        try:
            code, response = backend_order.trade(data)
            
        except Exception:
            code = 000
            response = "Internal Server Error. Check pyro traceback"
            print("Pyro traceback:")
            print(f"{''.join(Pyro5.errors.get_pyro_traceback())}")

    print(f"TRADE - {data} - {code} - {response}")
    return code

class TestService(unittest.TestCase):

   # TEST TRADE REQUEST
    def test_order_trade_function(self):

        print("\n\nTesting ORDER Trade requests\n")
        
        # Case 1: TEST CASE WITH CORRECT TRADE INFORMATION WITH SELL
        payload = {"name": "GameStart",
                    "quantity": 10,
                    "type": "sell"}
        self.assertTrue( call_order_trade_service(payload) == 200, "Trade request : Failed case 1")

        # Case 2: TEST CASE WITH CORRECT TRADE INFORMATION WITH BUY
        payload = {"name": "GameStart",
                    "quantity": 10,
                    "type": "buy"}
        self.assertTrue( call_order_trade_service(payload) == 200, "Trade request : Failed case 2")

        # Case 3: TEST CASE WITH CORRECT TRADE INFORMATION BUT WITH HIGH BUY VOLUME
        payload = {"name": "GameStart",
                    "quantity": 99999999999999999999999999999999,
                    "type": "buy"}
        self.assertTrue( call_order_trade_service(payload) == 500, "Trade request : Failed case 3")

        # Case 4: TEST CASE WITH INCORRECT STOCK NAME IN TRADE INFORMATION
        payload = {"name": "Hey",
                    "quantity": 10,
                    "type": "buy"}
        self.assertTrue( call_order_trade_service(payload) == 400, "Trade request : Failed case 4")

        # Case 5: TEST CASE WITH NEGATIVE QUANTITY IN TRADE INFORMATION
        payload = {"name": "MenhirCo",
                    "quantity": -10,
                    "type": "buy"}
        self.assertTrue( call_order_trade_service(payload) == 400, "Trade request : Failed case 5")

        # Case 6: TEST CASE WITH UNKNOWN TRADE TYPE IN TRADE INFORMATION
        payload = {"name": "MenhirCo",
                    "quantity": 10,
                    "type": "negotiate"}
        self.assertTrue( call_order_trade_service(payload) == 400, "Trade request : Failed case 6")

        # Case 7: TEST CASE WITH NO/INCORRECT TRADE INFORMATION
        payload = {"random": 10}
        self.assertTrue( call_order_trade_service(payload) == 400, "Trade request : Failed case 7")

        print("\nAll ORDER Trade requests ran successfully with expected responses")


if __name__ == "__main__":
    unittest.main()