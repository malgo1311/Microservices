# Evaluation

This folder contains `calc_latency.py` and `tester.sh`

`tester.sh` runs the client application and generates the log files. To run `tester.sh`

```
sh tester.sh
```

To run the server and generate its log files run the following command

```
nohup python3 server.py > ./server.log &
```

Do remember to kill them later on with the command

```
kill -9 [process id]
```

To run `calc_latency.py`

```
python3 calc_latency.py
```



