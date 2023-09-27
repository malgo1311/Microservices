## Contents

1) `catalog_service.py` has the implementation for the Catalog service with Lookup and Update method defined
2) `setup.py` has the configurable parameters like logging and file paths of the presistent locations for stock database and order transactions
3) `rw_lock` has the read-write lock implementation, this is not written by us
4) `run_catalog.sh` bash script to run the catalog service
5) `data` folder will contain the csv file for the stock db

## Steps to run ONLY Catalog service 

Run the following commands in the terminal

1) ```cd ../../``` - go to `src` directory
2) ```export PYTHON_ENV=<add-python-path>``` - add python environment path
3) ```./back-end/catalog_service/run_catalog.sh``` - run bash script

Example: export PYTHON_ENV=/Users/aishwarya/Aishwarya/Learning/venv/bin/activate