#!/usr/bin/env bash

#source /home/sahil/Desktop/Spring 23/677/lab/lab-1-asterix-and-the-stock-bazaar-venus/src/part2/lab1part2/bin/activate

cd /home/sahil/Desktop/Spring\ 23/677/lab/lab-1-asterix-and-the-stock-bazaar-venus/src/part2/
path="./eval/logs/2_tp/5_clients"
mkdir -p $path
for i in 1 2 3 4 5
do
    nohup python3 client.py > $path/$i.log &
    # nohup python3 client.py &

done
