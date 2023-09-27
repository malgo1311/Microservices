import os
import numpy as np
import pandas as pd

# Change this directory to your local directory to run it
# log_directory = "./src/client/eval/logs"
log_directory = "logs"

result_dict = {}
for folder_client in os.listdir(log_directory):
    result_dict[folder_client] = []

    for file in os.listdir(os.path.join(log_directory, folder_client)):

        
        file_path = os.path.join(log_directory, folder_client,file)

        file_text = open(file_path, mode = 'r')
        lines = file_text.readlines()
        file_text.close()
        all_times = []

        counter = 0
        for line in lines:    
            if 'Time ' in line:
                t = line.strip().split()
                all_times.append(float(t[5]))
                counter += 1

        avg_time = np.mean(all_times)
        result_dict[folder_client].append(avg_time)


print(result_dict)


print("-----------------")

final_dict = {}

for k, v in result_dict.items():
    final_dict[k] = []
    val = np.mean(v)
    final_dict[k].append(val)

for k,v in final_dict.items():

    print(str(k)+":"+ str(v))