
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




 Added source code to this directory. Part 1 is in *part1* directory and Part 2 is in *part2* directory

 Team Members: Aishwarya Malgonde, Sahil Jindal

 We owned each part individually - Aishwarya owned part1 and Sahil owned part2. We created our own branches and worked on them, and at the end, we merged them into the main branch. While working on our parts, we parallely brainstormed our approaches and collaborated on any issues and errors we encountered. We also worked on the documentation together and validated each other's contribution. Overall we ensured that both of us had a good understanding of the workings of both parts.

 Steps to run the system are in the `README.md` file inside the part1 and part2 folders


