# import libraries
import grpc
from concurrent import futures
import threading
import asterix_pb2_grpc
import asterix_pb2
from setup import *



class AsterixService(asterix_pb2_grpc.AsterixServicer):

    def __init__(self):
        # Initialize the lock
        self.lock  = threading.Semaphore(1)

    # Function to check if the server is running or not 
    def GetServerResponse(self, request, context):

        # get the string from the incoming request
        logger.debug(f'Getting Request from Client')
        message = request.message
        logger.debug(f'Request received')
        logger.info(f" Client pinged the server")
        
        # Curating the response
        result = f'Hello I am up and running received "{message}" message from you'
        result = {'message': result, 'received': True}
        
        logger.debug(f'Sending Response to Client')
        return asterix_pb2.MessageResponse(**result)

    # Lookup function to get the stock price
    def Lookup(self, request, context):
        
        logger.debug(f'Getting Request from Client')
        stockName = request.stockName
        logger.debug(f'Request received')
        
        logger.debug(f'Waititng to acquire lock')
        self.lock.acquire()             # acquire the lock
        logger.debug(f'Lock Acquired')

        # return stock price if stockName present in db
        logger.debug(f'Checking stock in Database')
        
        if stockName in stocksDB.keys(): 
            logger.info(f'{stockName} is present in Database')  # stock present in database
            value = float(stocksDB[stockName]["price"])         # returning the price of the stock

        # return -1 if stockName not present in db
        else:
            logger.info(f'{stockName} absent in Database') # stock absent in db
            value = float(-1)
        
        logger.info(f"Lookup request received for stockName - {stockName}. Message for client - {value}")
        result = {'price': value}

        self.lock.release()         # release the lock

        return asterix_pb2.Stockprice(**result)
    
    # Trade function to trade stocks
    def Trade(self,request,context):

        stockName = request.stockName   # name of the stock
        tradeNumber = request.N         # number of stocks to trade
        tradeType = request.type        # type of trade i.e buy or sell (Doesn't affect the functionality of code)

        logger.debug(f'Waititng to acquire lock')
        self.lock.acquire()             # acquire the lock
        logger.debug(f'Lock Acquired')
        
        
        # check if the stock is there
        logger.debug(f'Checking stock in Database')
        
        if(stockName in stocksDB.keys()): 
            logger.info(f'{stockName} is present in Database')     # stock present in db
            
            # check if stocks available for trading
            if stocksDB[stockName]['volume'] + tradeNumber <= stocksDB[stockName]['limit']:
                logger.info(f'{stockName} is available for trading')    # stock is available for trading
                stocksDB[stockName]['volume'] += tradeNumber
                response = 1        # trade successful
            
            # stock trade is suspended
            else:
                logger.info(f'Trade for {stockName} suspended')
                response = 0        # trade suspended

                
        # if stock not present
        else:
            logger.info(f'{stockName} absent in Database')
            response = -1           # stock not present in db so trade not possible

        logger.info(f"Trade request received for stockName - {stockName}. Message for client - {response}")
        logger.info("Updated Databse is :")
        logger.info(stocksDB)

        result = {'response':response}

        self.lock.release()         # release the lock

        return asterix_pb2.Success(**result)

    # update function to update stock prices
    def Update(self, request, context):
        stockName = request.stockName   # name of the stock in request
        price= request.price            # price of the stock

        logger.debug(f'Waititng to acquire lock')
        self.lock.acquire()             # acquire the lock
        logger.debug(f'Lock Acquired')

        
        # check stock validity
        logger.debug(f'Checking stock in Database')
        if(stockName in stocksDB.keys()):
            logger.info(f'{stockName} is present in Database')  # stock present in db
            
            # invalid price
            if(price<=0):
                logger.info(f'Invalid price for {stockName}')   
                response = -2                                   # invalid price response
            
            # update the stocksDB
            else:
                logger.info(f'Updating price of {stockName}')
                stocksDB[stockName]["price"] = price            # updating the price
                response = 1                                    # response when price gets updated

        # incorrect stock name response
        else:
            logger.info(f'{stockName} absent in Database')      
            response = -1                                       # response when stock is absent
        
        logger.info(f"Update request received for stockName - {stockName}. Message for client - {response}")
        logger.info("Updated Databse is :")
        logger.info(stocksDB)                                   # logging the stock database

        result = {'response':response}
        
        self.lock.release()                                     # releasing the lock

        return asterix_pb2.Success(**result)
        
def serve():
    # initiating the server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS), maximum_concurrent_rpcs = MAX_CONCURRENT_RPC) # configuration of the server defined in setup.py
    asterix_pb2_grpc.add_AsterixServicer_to_server(AsterixService(), server)
    server.add_insecure_port(str(HOST)+':'+str(PORT))
    server.start()                                      # starting the server
    logger.info('Server ready')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()