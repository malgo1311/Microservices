import re
import sys
import json
import time
import Pyro5.api
import Pyro5.errors
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
import redis

import rw_lock
import setup
logger = setup.logger

from replication_manager import OrderManager

# STARTING THE REDIS INSTANCE FOR IN MEMORY CACHING
_r = redis.Redis(host=setup.redis_host, port=setup.redis_port)

# FLUSHING REDIS CACHE AT SYSTEM START TIME 
_r.flushdb()

# SETTING REDIS CONFIG - MAXIMUM MEMORY AND EVICTION POLICY
_r.config_set("maxmemory", "10mb")
_r.config_set("maxmemory-policy", "volatile-ttl")
logger.info(f"Redis config : {_r.config_get('maxmemory')} - {_r.config_get('maxmemory-policy')}")

class FrontEndService(BaseHTTPRequestHandler):
    ''' CLASS DEFINES THE GET AND POST REQUEST OF OUR
    FRONT-END SERVICE '''

    # SETTING PROTOCOL VERSION FOR PERSISTENT CONNECTIONS
    protocol_version = 'HTTP/1.1'

    REP_MANAGER = OrderManager()

    # GETTING ORDER SERVICE LEADER
    ORDER_NS_LEADER = REP_MANAGER.get_leader()

    # INITIALIZING READ-WRITE LOCK
    RW_LOCK = rw_lock.RWLock()

    def _headers(self, code, response):
        ''' CONSTRUCTING HEADERS TO BE SENT WITH EVERY GET/POST RESPONSE '''

        if code != 200:

            # ERROR RESPONSE OUTPUT
            output = ({"error": {
                                "code": code,
                                "message": response
                            }
                    })
        else:
            output = response

        # CONVERTING JSON TO BYTES OBJECT FOR TODO
        output = json.dumps(output)
        output = output.encode("utf8")

        # ADDING RESPONSE CODE TO HEADER
        self.send_response(code)

        # DEFINING CONTENT-TYPE AS JSON, SINCE OUR RESPONSE IS IN JSON FORMAT
        self.send_header("Content-type", "application/json")

        # ADDITIONAL HEADERS FOR PERSISTENT CONNECTIONS (THREAD-PER-SESSION FEATURE)
        self.send_header("Connection", "keep-alive")
        self.send_header("Keep-Alive", "timeout=10")
        self.send_header("Content-Length", len(output))

        self.end_headers()

        return output


    def do_GET(self):
        ''' 
        DEFINING GET REQUEST FUNCTION
        ACCEPTABLE URL FORMATS -
        1. STOCK LOOKUP - /stocks/<stock_name>
        2. ORDER QUERY - /orders/<order_number>
        3. ORDER LEADER - /get_order_leader
        4. CACHE INVALIDATION - /cache_invalid/<stock_name>
        '''

        logger.info(f"Received GET request on url {self.path}")
        
        # GET function for stock lookup - /stocks/<stock_name>
        if re.match(r"^/stocks/[a-zA-Z]+$", self.path):

            # GETTING STOCK NAME FROM REQUEST URL
            stock_name = self.path.split('/')[-1]

            # Caching 
            logger.info("Checking Cache")
            try:
                # ACQUIRING READ LOCK FOR REDIS
                with FrontEndService.RW_LOCK.read_access:
                    cache_response = _r.get(stock_name)
            except Exception as err:
                logger.error(f"Redis error, cannot cache >>> {err}")
                cache_response = None
            logger.debug(f"Cache response - {cache_response}")
            
            if(cache_response):
                cache_response = json.loads(cache_response)
                logger.info("Getting cache response")
                if(cache_response=="Bad request. {stock_name} stock not found in db"):
                    code = 400
                    # final_response = self._headers(code,cache_response)
                    response = cache_response
                else:
                    code = 200
                    # final_response = self._headers(code,cache_response)
                    response = cache_response
                    logger.info(f"Got lookup response from cache - {response}")
            else:
                # CALLING LOOKUP FUNCTION FROM BACKEND - CATALOG SERVICE
                logger.info(f"Calling lookup service")
                with Pyro5.api.Proxy(f"PYRONAME:{setup.catalog_service_name}@{setup.catalog_ns_host}:{setup.catalog_ns_port}") as backend_catalog:
                    try:
                        code, response = backend_catalog.lookup(stock_name)
                        logger.info(f"Adding lookup response to cache")
                        try:
                            # ACQUIRING WRITE LOCK FOR REDIS
                            with FrontEndService.RW_LOCK.write_access:
                                _r.set(stock_name, json.dumps(response))
                                _r.expire(stock_name, setup.redis_ttl)
                        except Exception as err:
                            logger.error(f"Redis error, cannot cache >>> {err}")
                        
                    except Exception:
                        code = 500
                        response = "Internal Server Error. Check pyro traceback. From Front-end GET catalog lookup"
                        logger.error("Pyro traceback:")
                        logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")

            logger.info(f"Received lookup response - {code} {response}")

            # GENERATING FINAL RESPONSE WITH HEADERS
            final_response = self._headers(code, response)

            # SENDING RESPONSE TO CLIENT
            self.wfile.write(final_response)

        # GET FUNCTION FOR ORDER QUERY - /orders/<order_number>
        elif re.match(r"^/orders/[1-9][0-9]*$", self.path):

            # GETTING STOCK NAME FROM REQUEST URL
            order_number = int(self.path.split('/')[-1])

            # CALLING QUERY FUNCTION FROM BACKEND - ORDER SERVICE
            # INCASE LEADER FAILS, TRY LEADER ELECTION AND RESEND REQUEST THRICE
            max_try = 0
            pyro_fail = False
            while max_try < 3:
                logger.info(f"Calling order service for query")
                with Pyro5.api.Proxy(f"PYRONAME:{setup.order_service_name}@{setup.order_ns_host}:{FrontEndService.ORDER_NS_LEADER}") as backend_order:
                    try:
                        code, response = backend_order.query(order_number)
                        pyro_fail = False
                        break

                    # IF THE NAMESERVER DOESN'T RESPOND THEN CHOOSE A NEW LEADER
                    except Pyro5.errors.NamingError:
                        logger.error(f"{FrontEndService.ORDER_NS_LEADER} leader nameserver of backend order service down")
                        pyro_fail = True
                        
                    # IF THE SERVICE DOESN'T RESPOND THEN CHOOSE A NEW LEADER
                    except Pyro5.errors.CommunicationError:
                        logger.error(f"{FrontEndService.ORDER_NS_LEADER} leader of backend order service down")
                        pyro_fail = True

                    # THROW ERROR IF THERE IS SOME LOGICAL ERROR AND EXIT LOOP
                    except Exception:
                        code = 500
                        response = "Internal Server Error. Check pyro traceback. From Front-end GET order query"
                        logger.error("Pyro traceback:")
                        logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")
                        pyro_fail = False
                        break
                        
                        # max_try = sys.maxsize
                if pyro_fail:
                    max_try += 1
                    logger.info(f"Trying request again...")
                    time.sleep(2)
                    FrontEndService.ORDER_NS_LEADER = FrontEndService.REP_MANAGER.get_leader()

            logger.info(f"Received query response - {code} {response}")

            # GENERATING FINAL RESPONSE WITH HEADERS
            final_response = self._headers(code, response)

            # SENDING RESPONSE TO CLIENT
            self.wfile.write(final_response)

        # GET FUNCTION FOR LEADER - /get_order_leader
        elif "/get_order_leader" == self.path:
            
            logger.info(f"Processing GET request for get_order_leader")
            try:
                response = {"data": {"order_leader": FrontEndService.REP_MANAGER.get_curr_leader_number()}}
                code = 200
            except Exception as err:
                code = 500
                response = "Internal Server Error. Check get_order_leader logs"
                logger.error(f"Error in get_order_leader - {err}")

            # GENERATING FINAL RESPONSE WITH HEADERS
            final_response = self._headers(code, response)

            # SENDING RESPONSE TO CLIENT
            self.wfile.write(final_response)
        
        # GET FUNCTION FOR CACHE INVALIDATION - /cache_invalid/<stock_name>
        elif re.match(r"^/cache_invalid/[a-zA-Z]+$", self.path):
            
            stock_name = self.path.split('/')[-1]
            
            logger.info("Making Cache invalid")
            try:
                # ACQUIRING WRITE LOCK FOR REDIS
                with FrontEndService.RW_LOCK.write_access:
                    _r.delete(stock_name)
                code = 200
                response = {"data": "cache invalidation successful"}
                logger.info(f"Cache Invalidated in memory")
            except Exception as err:
                code = 500
                response = "Cache Invalidation unsuccessful. Check error log"
                logger.info(f"{response}")
                logger.error(f"Redis error, cannot cache >>> {err}")
            
            final_response = self._headers(code, response)

            # SENDING RESPONSE TO CLIENT
            self.wfile.write(final_response) 

         # RETURN ERROR IF INCORRECT URL
        else:
            message = "Invalid request url"
            logger.info(f"{message} - {self.path}")

            # GENERATING FINAL RESPONSE WITH HEADERS
            final_response = self._headers(404, message)

            # SENDING RESPONSE TO CLIENT
            self.wfile.write(final_response)

        logger.info(f"Finished GET request\n")

    
    def do_POST(self):
        '''
        DEFINING POST REQUEST FUNCTION
        ACCEPTABLE URL FORMAT - /orders
        '''

        logger.info(f"Received POST request on url {self.path}")
        
        # CHECK IF URL IS CORRECT
        if self.path == "/orders":
            
            # GETTING USER PAYLOAD ATTACHED TO POST REQUEST
            data = json.loads((self.rfile.read(int(self.headers['Content-Length']))))

            logger.debug(f'data - {data} {type(data)}')

            # CALLING TRADE FUNCTION FROM BACKEND - ORDER SERVICE
            # INCASE LEADER FAILS, TRY LEADER ELECTION AND RESEND REQUEST THRICE
            max_try = 0
            pyro_fail = False
            while max_try < 3:

                logger.info(f"Calling trade service")
                with Pyro5.api.Proxy(f"PYRONAME:{setup.order_service_name}@{setup.order_ns_host}:{FrontEndService.ORDER_NS_LEADER}") as backend_order:
                    try:
                        code, response = backend_order.trade(data)
                        pyro_fail = False
                        break

                    # IF THE NAMESERVER DOESN'T RESPOND THEN CHOOSE A NEW LEADER
                    except Pyro5.errors.NamingError:
                        code = 500
                        response = "Order leader's nameserver down. Please try after sometime"
                        logger.error(f"{FrontEndService.ORDER_NS_LEADER} leader nameserver of backend order service down")
                        pyro_fail = True
                        
                    # IF THE SERVICE DOESN'T RESPOND THEN CHOOSE A NEW LEADER
                    except Pyro5.errors.CommunicationError:
                        code = 500
                        response = "Order leader nameserver down. Please try after sometime"
                        logger.error(f"{FrontEndService.ORDER_NS_LEADER} leader of backend order service down")
                        pyro_fail = True

                    # THROW ERROR IF THERE IS SOME LOGICAL ERROR AND EXIT LOOP
                    except Exception:
                        code = 500
                        response = "Internal Server Error. Check pyro traceback. From Front-end POST"
                        logger.error("Pyro traceback:")
                        logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")
                        pyro_fail = False
                        break
                        
                # CHOOSING LEADER AGAIN INCASE THE CONNECTION FAILS
                if pyro_fail:
                    max_try += 1
                    logger.info(f"Trying request again...")
                    time.sleep(2)
                    FrontEndService.ORDER_NS_LEADER = FrontEndService.REP_MANAGER.get_leader()

            logger.info(f"Received trade response - {code} {response}")

            # GENERATING FINAL RESPONSE WITH HEADERS
            final_response = self._headers(code, response)

            # SENDING RESPONSE TO CLIENT
            self.wfile.write(final_response)
        
        # RETURN ERROR IF INCORRECT URL
        else:
            message = "Invalid request url"
            logger.info(f"{message}")

            # GENERATING FINAL RESPONSE WITH HEADERS
            final_response = self._headers(404, message)

            # SENDING RESPONSE TO CLIENT
            self.wfile.write(final_response)

        logger.info(f"Finished POST request\n")


def run_server(host = "localhost", port = 8000, threaded = False):
    '''FUNCTION TO RUN HTTP SERVER'''

    # SIMPLE HTTP SERVER
    if not threaded:
        httpd = HTTPServer((host, port), FrontEndService)
        logger.info(f"Starting httpd server on {host}:{port}\n")

    # THREADED HTTP SERVER
    else:
        httpd = ThreadingHTTPServer((host, port), FrontEndService)
        logger.info(f"Starting threaded httpd server on {host}:{port}\n")

    # STARTING HTTP SERVER
    httpd.serve_forever()


if __name__ == "__main__":

    # RUNS SERVER
    run_server(setup.host, setup.port, threaded = True)
