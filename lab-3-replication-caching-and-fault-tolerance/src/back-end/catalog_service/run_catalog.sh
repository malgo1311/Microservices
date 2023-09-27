#!/usr/bin/env bash

###################################
# This bash file is for starting catalog service
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

nohup python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9096 --bcport=9097 > logs/pyro_ns_9096.log &
export NS_PORT=9096
nohup python3 back-end/catalog_service/catalog_service.py > logs/catalog_9096.log &