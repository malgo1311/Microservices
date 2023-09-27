## Contents

1) `catalog_service` has all the files related to the Catalog service
2) `order_service` has all the files related to the Order service

## Steps to run the server

Run the following python commands in different terminal windows

1) ```cd ../../``` - go to root directory
2) First run the pyro nameserver - ```python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090```
3) Run catalog service - ```python3 src/back-end/catalog_service/catalog_service.py```
4) Run order service - ```python3 python3 src/back-end/order_service/order_service.py.py```

### You can run the files in background

```nohup python3 <file-name>.py > <log-name>.log &```