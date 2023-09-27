import grpc
import asterix_pb2_grpc
import asterix_pb2
from setup import *
import random 
import time

# update function to update the price of the stock
def update(stock,new_price):

    logger.debug(f'Waiting for connection to host:{HOST} and port:{PORT}')
    
    start = time.time()     # start the timer

    with grpc.insecure_channel(f'{HOST}:{PORT}') as channel:
        
        logger.debug(f'Trying Connection to Stub')

        stub = asterix_pb2_grpc.AsterixStub(channel)    # connecting to stub
        logger.debug(f'Getting response from server')
        
        response = stub.Update(asterix_pb2.UpdateInfo(stockName=stock,price=new_price))     # getting the response from the server
        
        # response received 
        logger.info(f'Client received: {response.response}')
    end = time.time()       # end the timer

    logger.info(f"Update: Time {end-start:.10f} sec")


if __name__ == "__main__":
    while True:         # run infinitely
        for stock in ['Hello World', 'GameStart', 'hey', 'FishCo', "BoarCo", "MenhirCo"]:
            price = random.randint(-100,100)    # generate random price
            logger.debug(f'Updating stock {stock}')
            update(stock,price)                 # update the stock price
        time.sleep(1)                           # wait for 1 second