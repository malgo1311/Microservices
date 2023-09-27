## Contents

1) `order_service.py` has the implementation for the Order service
2) `setup.py` has the configurable parameters like logging and file paths of the presistent locations for order log
3) `rw_lock` has the read-write lock implementation, this is not written by us
4) `run_replication.sh` bash script to run the replicated Order service
5) `data` folder will contain the csv file for the stock db
6) `ft_helper.py` helper scripts to sync the replicas at startup

## Steps to run ONLY Order service 

Run the following commands in the terminal

1) ```cd ../../``` - go to `src` directory
2) ```export PYTHON_ENV=<add-python-path>``` - add python environment path
3) ```./back-end/order_service/run_replication.sh``` - run bash script

Example: export PYTHON_ENV=/Users/aishwarya/Aishwarya/Learning/venv/bin/activate