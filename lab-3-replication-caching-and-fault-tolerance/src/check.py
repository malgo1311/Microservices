'''
import requests

url = f"http://0.0.0.0:8000/get_order_leader"

def sync():
    try: 
        # SENDING GET REQUEST OVER SESSION
        leader_ns_port = requests.get(url, timeout=5)
        print(leader_ns_port.text)

    except requests.exceptions.ConnectionError:
        print(f"NewConnectionError - Aborting - Frontend is not up!")

    except Exception as err:
        print(str(err))

sync()



import Pyro5.api
import Pyro5.errors

order_ns_host = "0.0.0.0"
order_service_name = "backend.order"

for ns_port in sorted([9094], reverse=True):
    uri = Pyro5.api.Proxy(f"PYRONAME:{order_service_name}@{order_ns_host}:{ns_port}")
    print(uri)
    with uri as p:
        try:
            test = p._pyroBind()
            print(f"YEP IT IS RUNNING! - {test}")
        except Pyro5.errors.NamingError: #Pyro5.errors.CommunicationError:
            print("NOPE IT IS NOT REACHABLE 1!")
        except Pyro5.errors.CommunicationError:
            print("NOPE IT IS NOT REACHABLE 2!")
        except:
            print("Pyro traceback:")
            print(f"{''.join(Pyro5.errors.get_pyro_traceback())}")
        # test = p._pyroBind()
        # print(f"IT IS - {test}")


# with open('leader.txt', "r") as fp:
#     for line in fp:
#         print(line, type(line))
'''
import pandas as pd

# df = pd.read_csv('back-end/order_service/data/order_log_9094.csv')
# print(type(df), isinstance(df, pd.DataFrame))
# df = df.to_dict()
# print(df)
# print()

# df = pd.DataFrame(df)
# # df = pd.read_json(df)
# print(df)

# df = None
# print(df.to_json())

df_2 = pd.read_csv('./back-end/order_service/data/order_log_9092.csv')
print(df_2)

temp_df = pd.DataFrame([[129, 'Ash', 'check', abs(11)]], columns=["transaction_number", "stock_name", "order_type", "trade_quantity"])
print(f"temp_df - {temp_df}")

df_2 = pd.concat([df_2, temp_df], ignore_index = True)
print(df_2)

# diff = df_2[df_2['transaction_number']>5]
# print(diff)

# new_df = pd.concat([df, diff], ignore_index=True) #df.append(diff)
# print(new_df)
