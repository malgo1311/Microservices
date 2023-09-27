## Contents

1) `catalog_service` has all the files related to the Catalog service
2) `order_service` has all the files related to the Order service

## Steps to run ONLY Order service 

Run the following commands in the terminal

1) ```cd ../``` - go to `src` directory
2) ```export PYTHON_ENV=<add-python-path>``` - add python environment path
3) ```./back-end/order_service/run_replication.sh``` - run bash script

## Steps to run ONLY Catalog service 

Run the following commands in the terminal

1) ```cd ../``` - go to `src` directory
2) ```export PYTHON_ENV=<add-python-path>``` - add python environment path
3) ```./back-end/catalog_service/run_catalog.sh``` - run bash script

Example: export PYTHON_ENV=/Users/aishwarya/Aishwarya/Learning/venv/bin/activate