#!/usr/bin/env bash

###################################
# This bash file is for running the backend
###################################

# PLEASE ADD ENV VARIABLE GIVING THE PYTHON ENVIRONMENT FILE
# export PYTHON_ENV="/Users/aishwarya/Aishwarya/Learning/venv/bin/activate"
# ############################# IMPORTANT #################################

# CREATING LOGS DIRECTORY
if [ ! -d logs ]
then
    mkdir logs
    echo "Creating logs directory"
fi

# START ORDER SERVICE
./back-end/order_service/run_replication.sh

# START CATALOG SERVICE
./back-end/catalog_service/run_catalog.sh

# WAITING FOR BACKEND TO START
sleep 4

# START FRONTEND SERVICE
./front-end/run_frontend.sh
