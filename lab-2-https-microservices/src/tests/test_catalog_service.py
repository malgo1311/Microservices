import unittest
import requests
import Pyro5.api
import Pyro5.errors

catalog_service_name = "backend.catalog"
catalog_ns_host = "0.0.0.0"
catalog_ns_port = "9090"

# FUNCTION TO CALL CATALOG LOOKUP SERVICE
def call_catalog_lookup_service(stock_name):

    with Pyro5.api.Proxy(f"PYRONAME:{catalog_service_name}@{catalog_ns_host}:{catalog_ns_port}") as backend_catalog:
        try:
            code, response = backend_catalog.lookup(stock_name)
        except Exception:
            code = 500
            response = "Internal Server Error. Check pyro traceback"
            print("Pyro traceback:")
            print(f"{''.join(Pyro5.errors.get_pyro_traceback())}")

    print(f"Lookup - {stock_name} - {code} - {response}")
    return code

# FUNCTION TO CALL CATALOG UPDATE SERVICE
def call_catalog_update_service(stock_name, update_quantity):

    with Pyro5.api.Proxy(f"PYRONAME:{catalog_service_name}@{catalog_ns_host}:{catalog_ns_port}") as backend_catalog:
        try:
            code, message = backend_catalog.update(stock_name, update_quantity)
        except Exception:
            code = 500
            message = "Internal Server Error. Check pyro traceback."
            print("Pyro traceback:")
            print(f"{''.join(Pyro5.errors.get_pyro_traceback())}")

    print(f"Update - {stock_name}, {update_quantity} - {code} - {message}")
    return code

class TestService(unittest.TestCase):

    # TEST LOOKUP REQUEST
    def test_catalog_lookup_function(self):

        print("\n\nTesting Catalog Lookup requests\n")
        
        # Case 1: TEST CASE WITH CORRECT STOCK NAME
        stock_name = "FishCo"
        self.assertTrue( call_catalog_lookup_service(stock_name) == 200, "Lookup request : Failed case 1")

        # Case 2: TEST CASE WITH INCORRECT STOCK NAME
        stock_name = "Ash"
        self.assertTrue( call_catalog_lookup_service(stock_name) == 400, "Lookup request : Failed case 2")

        print("\nAll Catalog Lookup requests ran successfully which expected responses")

    # TEST UPDATE REQUEST
    def test_catalog_update_function(self):

        print("\n\nTesting Catalog Update requests\n")
        
        # Case 1: TEST CASE WITH CORRECT STOCK NAME AND QUANTIY
        stock_name = "FishCo"
        update_quantity = 10
        self.assertTrue( call_catalog_update_service(stock_name, update_quantity) == 200, "Update request : Failed case 1")

        # Case 2: TEST CASE WITH CORRECT STOCK NAME AND INCORRECT QUANTIY
        stock_name = "FishCo"
        update_quantity = "LOL"
        self.assertTrue( call_catalog_update_service(stock_name, update_quantity) == 500, "Update request : Failed case 2")

        # Case 3: TEST CASE WITH INCORRECT STOCK NAME AND CORRECT QUANTIY
        stock_name = "Meh"
        update_quantity = 10
        self.assertTrue( call_catalog_update_service(stock_name, update_quantity) == 400, "Update request : Failed case 3")

        print("\nAll Catalog Update requests ran successfully with expected responses")


if __name__ == "__main__":
    unittest.main()