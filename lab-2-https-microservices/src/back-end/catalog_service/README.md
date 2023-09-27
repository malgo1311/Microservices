## Contents

1) `catalog_service.py` has the implementation for the Catalog service with Lookup and Update method defined
2) `setup.py` has the configurable parameters like logging and file paths of the presistent locations for stock database and order transactions
3) `rw_lock` has the read-write lock implementation, this is not written by us
4) `Dockerfile` has the configurations to containerize the Catalog service
5) `run.sh` entrypoint run file for the docker image

## Steps to run the server

Run the following python commands in different terminal windows

1) First run the pyro nameserver - ```python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090```
1) ```cd ../../../``` - go to root directory
2) Run catalog service - ```python3 src/back-end/catalog_service/catalog_service.py```

## Steps to run the Catalog service solely with Dockerfile

1) docker build . -t catalog
2) docker run -h catalog -p 9090:9090 -v `pwd`/data:/app/data catalog

### You can run the files in background

```nohup python3 <file-name>.py > <log-name>.log &```