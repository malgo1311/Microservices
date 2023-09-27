#!/usr/bin/env bash

###################################
# This bash file is for starting order service with replication
###################################

# CREATING LOGS DIRECTORY
if [ ! -d logs ]
then
    mkdir logs
    echo "Creating logs directory"
fi

# ACTIVATING LOCAL MACHINE PYTHON ENVIRONMENT
# source /Users/aishwarya/Aishwarya/Learning/venv/bin/activate
source ${PYTHON_ENV}

nohup python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090 --bcport=9091 > logs/pyro_ns_9090.log &
export NS_PORT=9090
nohup python3 back-end/order_service/order_service.py > logs/order_9090.log &

nohup python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9092 --bcport=9093 > logs/pyro_ns_9092.log &
export NS_PORT=9092
nohup python3 back-end/order_service/order_service.py > logs/order_9092.log &

# nohup python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9094 --bcport=9095 > logs/pyro_ns_9094.log &
# export NS_PORT=9094
# nohup python3 back-end/order_service/order_service.py > logs/order_9094.log &