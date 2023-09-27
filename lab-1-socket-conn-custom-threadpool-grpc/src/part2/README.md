# Part 2

## File system -

1) `client.py` has the client side implementation, sending sequential requests to the server for Lookup and Trade method
2) `client_update.py` has the client side implementation, sending sequential requests to the server for Update method
3) `server.py` has the server side implementation, receiving & processing client request
4) `process.py` has the threadpool and queue implementation
5) `setup.py` has the configurable parameters like host name, port number, number of threads in the threadpool and stock database
6) `eval` folder has the evaluation scripts
7) `asterix.proto` is the  method definition

## Steps to run the server

1) Compile .proto file - python3 -m grpc_tools.protoc --proto_path=. ./asterix.proto --python_out=. --grpc_python_out=.
Above command will generate `asterix_pb2_grpc.py` and `asterix_pb2.py` files.
2) Configure HOST and PORT in setup.py on server and client side
3) Run server - ```python3 server.py```
4) Run client - ```python3 client.py```
5) Run update client - ```python3 client_update.py```