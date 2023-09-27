## Contents

1) `order_service.py` has the implementation for the order service with Trade method defined
2) `setup.py` has all the configurable parameters like logging and file paths of the presistent locations for order log
3) `Dockerfile` has the configurations to containerize the Catalog service
4) `run.sh` entrypoint run file for the docker image

## Steps to run the server

Run the following python commands in different terminal windows

1) First run the pyro nameserver - ```python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090```
1) ```cd ../../../``` - go to root directory
2) Run order service - ```python3 src/back-end/order_service/order_service.py```

## Steps to run the Order service solely with Dockerfile

1) docker build . -t order
2) docker run -h order -p 9090:9090 -v `pwd`/data:/app/data order

### You can run the files in background

```nohup python3 <file-name>.py > <log-name>.log &```