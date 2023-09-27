import grpc
import asterix_pb2_grpc
import asterix_pb2
from setup import *
import random
import time


# NOTE(gRPC Python Team): .close() is possible on a channel and should be
# used in circumstances in which the with statement does not fit the needs
# of the code.

# Function to ping the server and see if it is active
def GetServerResponse():
    ## GetServerResponse
    request_message = "Hello Server you there?"                             # Request message to server        
    logger.debug(f'Waiting for connection to host:{HOST} and port:{PORT}')  
    with grpc.insecure_channel(f'{HOST}:{PORT}') as channel:    
        logger.debug(f'Trying Connection to Stub')
        stub = asterix_pb2_grpc.AsterixStub(channel)                        # Trying to connect to a channel
        logger.debug(f'Getting response from server')
        response = stub.GetServerResponse(asterix_pb2.Message(message=request_message))     # Getting a response from server
        logger.info(f'Client received: {response.message}')

def Lookup(stock):
    ## Lookup request function
    logger.debug(f'Waiting for connection to host:{HOST} and port:{PORT}')
    start = time.time()     # start the timer
    with grpc.insecure_channel(f'{HOST}:{PORT}') as channel:
        logger.debug(f'Trying Connection to Stub')
        stub = asterix_pb2_grpc.AsterixStub(channel)                        # Trying to connect to the channel
        logger.debug(f'Getting response from server')
        response = stub.Lookup(asterix_pb2.Stockname(stockName=stock))      # Getting the response from the server
        logger.info(f'Client received: {response.price}')
    
    end = time.time()       # end the timer
    logger.info(f"Lookup: Time {end-start:.10f} sec")

def Trade(stock,stockCount,type):
    ## Trade request function
    logger.debug(f'Waiting for connection to host:{HOST} and port:{PORT}')
    
    start = time.time()     # start the timer
    with grpc.insecure_channel(f'{HOST}:{PORT}') as channel:
        logger.debug(f'Trying Connection to Stub')
        stub = asterix_pb2_grpc.AsterixStub(channel)        # Trying to connect to the channel
        logger.debug(f'Getting response from server')
        response = stub.Trade(asterix_pb2.TradeInfo(stockName=stock , N=stockCount , type=type))    # Getting the response from the server
        logger.info(f'Client received: {response.response}')    # response received 
    end = time.time()       # end the timer
    logger.info(f"Trade: Time {end-start:.10f} sec")  


if __name__ == '__main__':
    
    # logger.debug(f'Checking Server Conection')
    # GetServerResponse()
    
    # ---------------------- Lookup driver code --------------------------
    """uncomment the following code if you want to send the lookup requests"""
    # for stock in ['Hello World', 'GameStart', 'hey', 'FishCo',"BoarCo","MenhirCo"]:
    #     logger.debug(f'Looking for stock {stock}')
    #     Lookup(stock)
    
    # ---------------------- Trade driver code ---------------------------
    """uncomment the following code if you want to send the trade requests"""
    # for i in range(QUERYCOUNT):
    #     for stock in ['Hello World', 'GameStart', 'hey', 'FishCo',"BoarCo","MenhirCo"]:
    #         stockCount = random.randint(-100,100)
    #         logger.debug(f'Buying {stockCount} shares of {stock}')
    #         Trade(stock,stockCount,"buy")

    # ---------------------- Random Trade/Lookup driver code ---------------------------
    """uncomment the following code if you want to randomly send either a trade request or a lookup request"""

    for i in range(QUERYCOUNT):
        for stock in ['Hello World', 'GameStart', 'hey', 'FishCo',"BoarCo","MenhirCo"]:

            flag = random.randint(0, 1)

            if flag == 0:

                logger.debug(f'Looking for stock {stock}')
                Lookup(stock)

            else:

                stockCount = random.randint(-100,100)
                logger.debug(f'Buying {stockCount} shares of {stock}')
                Trade(stock,stockCount,"buy")