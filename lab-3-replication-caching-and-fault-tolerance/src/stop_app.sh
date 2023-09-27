#!/usr/bin/env bash

###################################
# This bash file is to stop replication
###################################

kill -9 $(pgrep -f Pyro5.nameserver)
kill -9 $(pgrep -f order_service.py)
kill -9 $(pgrep -f catalog_service.py)
kill -9 $(pgrep -f frontend_service.py)

sudo systemctl restart redis.service
