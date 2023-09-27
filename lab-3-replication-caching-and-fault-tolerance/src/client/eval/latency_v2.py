import os
import numpy as np
import pandas as pd

# Change this directory to your local directory to run it
# log_directory = "./src/client/eval/logs"
log_directory = "logs"

result_dict = {}
for folder_client in os.listdir(log_directory):
    result_dict[folder_client] = {"lookup_time": [],
                                  "trade_time": [],
                                  "query_time": []}

    for file in os.listdir(os.path.join(log_directory, folder_client)):

        
        file_path = os.path.join(log_directory, folder_client,file)

        file_text = open(file_path, mode = 'r')
        lines = file_text.readlines()
        file_text.close()
        all_times = []
        lookup_time = []
        trade_time = []
        query_time = []

        for line in lines:    
            t = line.strip().split()

            if 'Lookup : Time ' in line:
                # print(t)
                lookup_time.append(float(t[5]))

            elif 'Trade : Time ' in line:
                trade_time.append(float(t[5]))

            elif 'Query : Time ' in line:
                query_time.append(float(t[5]))

        result_dict[folder_client]["lookup_time"].append(np.mean(lookup_time))
        result_dict[folder_client]["trade_time"].append(np.mean(trade_time))
        result_dict[folder_client]["query_time"].append(np.mean(query_time))


print(result_dict)


print("-----------------")

final_dict = {}

for k, v in result_dict.items():
    # final_dict[k] = {}
    val = {"lookup_time": np.mean(v['lookup_time']),
            "trade_time": np.mean(v['trade_time']),
            "query_time": np.mean(v['query_time'])}
    final_dict[k] = val

print(f"x_client: lookup_time \t\t trade_time \t\t query_time")
for k,v in final_dict.items():
    print(str(k)+": "+ str(v['lookup_time']) + " \t " + str(v['trade_time']) + " \t " + str(v['query_time']))