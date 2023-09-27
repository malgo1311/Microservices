## Contents

1) `tester.sh` -  This shell script runs multiple `client.py` in background and also generates the log files for each of the clients
2) `twin_tester.sh` - This shell script runs multiple `client_lookup.py` in background and also generates the log files for each of the clients
3) `latency.py` this file calculates the avarage latency of each client using the log files which we create using `tester.sh` 


## To run each file

```python3 latency.py```
```sh tester.sh```
```sh twin_tester.sh```
