import sys
import Pyro5.api
import Pyro5.errors

import setup
logger = setup.logger

# IMPORTING READ-WRITE LOCK
import rw_lock

class OrderManager():

    # INITIALIZING ORDER LEADER
    CURRENT_LEADER = None

    # INITIALIZING READ-WRITE LOCK
    RW_LOCK = rw_lock.RWLock()

    # ELECTING ORDER SERVICE LEADER
    def get_leader(self):

        leader_found = None
        
        # CHECKING WITH THE ID NUMBER IS DESCENDING ORDER
        for ns_port in sorted(setup.replicated_order_ns, reverse=True):

            # CALLING HEALTH CHECK FUNCTION FROM BACKEND - ORDER SERVICE
            logger.info(f"Calling ping (health check) service for {ns_port} order")
            with Pyro5.api.Proxy(f"PYRONAME:{setup.order_service_name}@{setup.order_ns_host}:{ns_port}") as backend_order:

                try:
                    # response = backend_order.health_check()
                    response = backend_order._pyroBind()

                # INCASE THE NAMESERVER OF THE BACKEND SERVICE IS DOWN
                except Pyro5.errors.NamingError:
                    response = False
                    logger.info(f"Health check failed for {ns_port} order")

                # INCASE THE BACKEND SERVICE IS DOWN
                except Pyro5.errors.CommunicationError:
                    response = False
                    logger.info(f"Health check failed for {ns_port} order")

                # SHOW TRACEBACK INCASE OF LOGICAL ERROR
                except Exception:
                    response = False
                    logger.error("Pyro traceback:")
                    logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")
                    # continue

            # if response == "OK":
            if response:
                logger.info(f"Order service leader found - {ns_port} order")
                leader_found = ns_port
                break

        # ABORTING FRONT-END SERVICE IF NO ORDER REPLICA FOUND
        if not leader_found:
            logger.info(f"Order service leader NOT found. Aborting frontend service")
            sys.exit()

        # NOTIFYING ALL ALIVE REPLICAS ABOUT THE LEADER
        else:
            self.__notify_replicas(leader_found)

        # ACQUIRING WRITE LOCK
        with OrderManager.RW_LOCK.write_access:
            OrderManager.CURRENT_LEADER = leader_found

        return leader_found

    # NOTIFY OTHER REPLICAS ABOUT THE LEADER
    def __notify_replicas(self, leader):

        # NOTIFYING ALL THE REPLICAS ABOUT THE LEADER
        for ns_port in setup.replicated_order_ns:

            # CALLING NOTIFY FUNCTION FROM BACKEND - ORDER SERVICE
            logger.info(f"Notifying {ns_port} replica of order leader")
            with Pyro5.api.Proxy(f"PYRONAME:{setup.order_service_name}@{setup.order_ns_host}:{ns_port}") as backend_order:
            
                try:
                    response = backend_order.leader_notification(leader)

                # INCASE THE NAMESERVER OF THE BACKEND SERVICE IS DOWN
                except Pyro5.errors.NamingError:
                    response = f"Cannot reach {ns_port} replica - nameserver down"
                    logger.error(f"{response}")

                # INCASE THE BACKEND SERVICE IS DOWN
                except Pyro5.errors.CommunicationError:
                    response = f"Cannot reach {ns_port} replica - service down"
                    logger.error(f"{response}")

                # SHOW TRACEBACK INCASE OF LOGICAL ERROR
                except Exception:
                    logger.error("Pyro traceback:")
                    logger.error(f"{''.join(Pyro5.errors.get_pyro_traceback())}")

        return

    # GET THE LEADER ID NUMBER
    def get_curr_leader_number(self):

        logger.info(f"Getting current order leader")
        # ACQUIRING READ LOCK
        with OrderManager.RW_LOCK.read_access:
            leader = OrderManager.CURRENT_LEADER
        logger.info(f"Current order leader is {leader}")

        return leader