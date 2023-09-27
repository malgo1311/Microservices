## Contents

1) `frontend_service.py` has the has the code for the threaded http server
2) `setup.py` has the configurable parameters like logging, host name and port number
3) `rw_lock` has the read-write lock implementation, this is not written by us
4) `run_frontend.sh` bash script to run the Frontend service
5) `replication_manager.py` helper script for managing the Order replicas

## To run the front-end server

1) Start redis server in background
2) ```cd ../``` - go to `src` directory
3) ```export PYTHON_ENV=<add-python-path>``` - add python environment path
4) ```./front-end/run_frontend.sh``` - run bash script

Example: export PYTHON_ENV=/Users/aishwarya/Aishwarya/Learning/venv/bin/activate