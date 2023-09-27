## Contents

1) `service.py` has the has the code for the threaded http server
2) `setup.py` has the configurable parameters like logging, host name and port number
3) `Dockerfile` has the configurations to containerize the Frontend service
4) `run.sh` entrypoint run file for the docker image

## To run the front-end server

1) ```cd ../../``` - go to root directory
2) ```python3 src/front-end/service.py```

## Steps to run the Frontend service solely with Dockerfile

1) docker build . -t frontend
2) docker run -p 8000:8000 frontend

Note: You can run the python files in background like this - ```nohup python3 <file-name>.py > <log-name>.log &```