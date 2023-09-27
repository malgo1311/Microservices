#############################
# This bash file is for Dockerfile
# Don't run it as it is
##########################
export USING_DOCKER=True

nohup python3 -m Pyro5.nameserver --host="0.0.0.0" --port=9090 > pyro_ns.log &

python3 order_service.py