## Contents

1) `test_catalog_service.py` - runs test cases for Catalog service
2) `test_order_service.py` - runs test cases for Order service
3) `test_frontend_service.py` - runs test cases for Frontend service (this tests the overall server - Frontend+Backend)

## To run the catalog test case

1) ```nohup python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090 > pyro_ns.log &```
2) Go to root directory of the repository
3) ```nohup python3 src/back-end/catalog_service/catalog_service.py > catalog.log &```
4) Go to ```cd src/tests``` directory
5) ```python3 test_catalog_service.py```

## To run the order test case

1) ```nohup python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090 > pyro_ns.log &```
2) Go to root directory of the repository
3) ```nohup python3 src/back-end/order_service/order_service.py > order.log &```
4) ```nohup python3 src/back-end/catalog_service/catalog_service.py > catalog.log &```
5) Go to ```cd src/tests``` directory
6) ```python3 test_order_service.py```

## To run the frontend test case

1) ```nohup python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090 > pyro_ns.log &```
2) Go to root directory of the repository
3) ```nohup python3 src/front-end/service.py > frontend.log &```
4) Go to ```cd src/tests``` directory
5) ```python3 test_frontend_service.py```

Note: You can run the python files in background like this - ```nohup python3 <file-name>.py > <log-name>.log &```