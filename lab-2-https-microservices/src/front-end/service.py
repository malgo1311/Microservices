import re
import json
import Pyro5.api
import Pyro5.errors
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer

import setup
logger = setup.logger


class FrontEndService(BaseHTTPRequestHandler):
    ''' CLASS DEFINES THE GET AND POST REQUEST OF OUR
    FRONT-END SERVICE '''

    
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
        ACCEPTABLE URL FORMAT - /stocks/<stock_name>
        '''

        logger.info(f"Received GET request on url {self.path}")
        
        # CHECK IF URL IS IN CORRECT FORMAT
        if re.match(r"^/stocks/[a-zA-Z]+$", self.path):

            # GETTING STOCK NAME FROM REQUEST URL
            stock_name = self.path.split('/')[-1]

            # CALLING LOOKUP FUNCTION FROM BACKEND - CATALOG SERVICE
            logger.info(f"Calling lookup service")
            with Pyro5.api.Proxy(f"PYRONAME:{setup.catalog_service_name}@{setup.catalog_ns_host}:{setup.catalog_ns_port}") as backend_catalog:
                try:
                    code, response = backend_catalog.lookup(stock_name)
                except Exception:
                    code = 500
                    response = "Internal Server Error. Check pyro traceback. From Front-end GET"
                    logger.error("Pyro traceback:")
                    logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")

            logger.info(f"Received lookup response - {code} {response}")

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
            logger.info(f"Calling trade service")
            with Pyro5.api.Proxy(f"PYRONAME:{setup.order_service_name}@{setup.order_ns_host}:{setup.order_ns_port}") as backend_order:
                try:
                    code, response = backend_order.trade(data)
                    
                except Exception:
                    code = 500
                    response = "Internal Server Error. Check pyro traceback. From Front-end POST"
                    logger.error("Pyro traceback:")
                    logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")

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
