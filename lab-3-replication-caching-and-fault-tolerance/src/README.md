# README

Team Members: Aishwarya Malgonde, Sahil Jindal

We owned each part individually - Aishwarya owned part2 + part3 and Sahil owned part1 + part4. We created our own branches and worked on them, and at the end, we merged them into the main branch. While working on our parts, we parallely brainstormed our approaches and collaborated on any issues and errors we encountered. We also worked on the documentation together and validated each other's contribution. Overall we ensured that both of us had a good understanding of the workings of both parts.

### Install Dependencies
```
To run code your machine should have `python3` and `pip3` installed
```

```
pip3 install -r requirements.txt
```

```
Install redis server - https://tableplus.com/blog/2018/10/how-to-start-stop-restart-redis.html
```

## Contents

1) `back-end` folder has the code for catalog and order service
2) `client` folder has the code for running clients
3) `front-end` folder has the code for the frontend threaded http server
4) `test` folder has the code for test cases for each of the three service

Assumption: We assume that the terminals are started in the current `src` directory

### Run the application using bash scripts

1) Start redis server in background
2) ```export PYTHON_ENV=<add-python-path>``` - add python environment path
3) ```./start_app.sh``` - starts frontend + backend services
4) ```./stop_app.sh``` - stops frontend and/or backend services

### Run client

```cd client```
```python3 client.py``` - to run single client 
```./eval/tester.sh``` - to run multiple clients

Note 1: ```chmod +x <file-name>.sh``` - For bash scripts, run this if getting Permission denied error 


## AWS Setup

Change ```~/.aws/credentials``` and download the pem file according to lablet 5

Use ```aws configure``` command to configure the aws and set region name and output format

Now in the root directory use the command `aws ec2 run-instances --image-id ami-0044130ca185d0880 --instance-type m5a.large --key-name vockey > instance.json`. This command will start a m5a.large instance and install ubuntu 22.04 LTS on it.

Open the port ```aws ec2 authorize-security-group-ingress --group-name default --protocol tcp --port 8000 --cidr 0.0.0.0/0```

Use ```aws ec2 describe-instances --instance-id <your-instance-id>``` to get the public DNS 

using the public dns of the instace ssh to it using the command ```ssh -i labsuser.pem ubuntu@<your-instance's-public-DNS-name>```

### Now install softwares

```sudo apt update```

```sudo apt install redis-server```

```sudo nano /etc/redis/redis.conf```

Inside the file, find the supervised directive. This directive allows you to declare an init system to manage Redis as a service, providing you with more control over its operation. The supervised directive is set to no by default. Since you are running Ubuntu, which uses the systemd init system, change this to systemd

```sudo systemctl status redis```

The redis server should start on 6379 port

Use the following command to restart redis service
```sudo systemctl restart redis.service```

install pip

```sudo apt install python3-pip```

Install the libraries

```pip3 install Pyro5```
```pip3 install pandas```
```sudo pip install redis```

We can save the image of this instance so that we dont have to create it from scratch.
