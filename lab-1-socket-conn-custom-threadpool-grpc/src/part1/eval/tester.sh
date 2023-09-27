#!/usr/bin/env bash

source /Users/aishwarya/Aishwarya/Learning/venv/bin/activate
cd /Users/aishwarya/github-classroom/umass-cs677-current/lab-1-asterix-and-the-stock-bazaar-venus/src/part1
# path="./eval/logs/4_tp/3_clients"
# mkdir $path
for i in 1 2
do
    # nohup python3 client.py > $path/$i.log &
    nohup python3 client.py &
done