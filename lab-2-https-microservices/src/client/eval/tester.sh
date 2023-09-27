#!/usr/bin/env bash

cd ./src/client

num_clients=5

path="./eval/logs/${num_clients}_client"
echo "${path}"
if [ ! -d "${path}" ] 
then
    echo "Making Directory ${path}"
    mkdir -p $path
else
    echo "Directory ${path} present"
fi

for j in `seq 1 $num_clients`
do
    nohup python3 client.py > $path/$j.log &
done

