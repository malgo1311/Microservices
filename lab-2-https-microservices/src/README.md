# README

Team Members: Aishwarya Malgonde, Sahil Jindal

We owned each part individually - Aishwarya owned part1 and Sahil owned part2 + part3. We created our own branches and worked on them, and at the end, we merged them into the main branch. While working on our parts, we parallely brainstormed our approaches and collaborated on any issues and errors we encountered. We also worked on the documentation together and validated each other's contribution. Overall we ensured that both of us had a good understanding of the workings of both parts.

To run code your machine should have `python3` and `pip3` installed

### Install Dependencies

```
pip3 install -r requirements.txt
```

## Contents

1) `back-end` folder has the code for catalog and order service
2) `client` folder has the code for running clients
3) `data` folder stores csv files for the stock database and order logs
4) `front-end` folder has the code for the frontend threaded http server

Assumption: We assume that the terminals are started in the current directory

## How to run the entire service with docker

### Run the following commands in different terminal

1) Run the server

```cd ../``` - go to root directory

``` docker-compose up --build``` -  build and run the docker using docker compose

2) Run the client

```cd client```

```python3 client.py``` - to run single client

```sh ./eval/tester.sh``` - to run multiple clients


## How to run the entire service without docker

### Run the following python commands in background in one terminal window

1) ```cd ../``` - run all commands from root directory
2) ```nohup python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090 > pyro_ns.log &``` - starts the Pyro name server
3) ```nohup python3 src/back-end/catalog_service/catalog_service.py > catalog.log &``` - starts the Catalog service
4) ```nohup python3 src/back-end/order_service/order_service.py > order.log &``` - starts the Order service
5) ```nohup python3 src/front-end/service.py > frontend.log &``` - starts the Frontend service
6) ```nohup python3 src/client/client.py > client.log &``` - runs client

### Run the following python commands in different terminal windows

1) Run front-end service

```cd ../``` - go to root directory

```python3 src/front-end/service.py```

2) Run back-end service

```cd ../``` - go to root directory

```python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090``` - first run the pyro nameserver

```python3 src/back-end/catalog_service/catalog_service.py``` - runs catalog service

```python3 src/back-end/order_service/order_service.py``` - runs order service

3) Run client

```cd client```

```python3 client.py``` - to run single client 

```sh ./eval/tester.sh``` - to run multiple clients



Note 1: ```chmod +x run_clients.sh``` - run only once before the very first run

Note 2: Please update python environment path and the working folder path in the run_clients.sh file to run multiple clients

Note 3: You can run the python files in background like this - ```nohup python3 <file-name>.py > <log-name>.log &```
