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

# START FRONTEND SERVICE
nohup python3 front-end/frontend_service.py > logs/frontend.log &