# Part 1

## File system -

1) `client.py` has the client side implementation, sending sequential requests to the server
2) `server.py` has the server side implementation, receiving & processing client request
3) `process.py` has the threadpool and queue implementation
3) `setup.py` has the configurable parameters like host name, port number, number of threads in the threadpool and stock database
4) `eval` folder has the evaluation scripts

## Steps to run the server

1) Configure PORT in setup.py on server side
2) Run server - ```python3 server.py```
3) Check server host name/address printed in the logs after running step 2, and update HOST and PORT in `setup.py` on client side
4) Run client - ```python3 client.py```