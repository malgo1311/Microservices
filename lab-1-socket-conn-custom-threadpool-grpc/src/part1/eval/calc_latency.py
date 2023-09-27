import os
import numpy as np

log_directory = "/Users/aishwarya/github-classroom/umass-cs677-current/lab-1-asterix-and-the-stock-bazaar-venus/src/part1/eval/logs/"
print(os.listdir(log_directory))

result_dict = {}

for folder_tp in os.listdir(log_directory):
    result_dict[folder_tp] = {}

    for folder in os.listdir(os.path.join(log_directory, folder_tp)):
        result_dict[folder_tp][folder] = []

        for file in os.listdir(os.path.join(log_directory, folder_tp, folder)):

            file_path = os.path.join(log_directory, folder_tp, folder, file)

            file_text = open(file_path, mode = 'r')
            lines = file_text.readlines()
            file_text.close()
            all_times = []

            counter = 0
            for line in lines:
                # line = line.split(',')
                # line = [i.strip() for i in line]
                if 'Time ' in line:
                    t = line.strip().split()
                    all_times.append(float(t[5]))
                    counter += 1

                if counter == 500:
                    break
            
            avg_time = np.mean(all_times)
            result_dict[folder_tp][folder].append(avg_time)

            # print(all_times)
            # print(f'{folder_tp} : {folder} : {file} : {avg_time:.7f} secs {len(all_times)} requests')
        #     break
        # break

print('here')
print(result_dict)

import pandas as pd

df_final = pd.DataFrame(columns=['1_tp', '2_tp', '3_tp', '4_tp', '5_tp'])

final_dict = {}

for k, _ in result_dict.items():
    print(f"{k}")
    final_dict[k] = []
    for k2, v in result_dict[k].items():
            val = np.mean(v)
            print(f"{k2} {val:.7f}")
            final_dict[k].append(val)

            if '1' in k2: index_position = 0
            elif '2' in k2: index_position = 1
            elif '3' in k2: index_position = 2
            elif '4' in k2: index_position = 3
            elif '5' in k2: index_position = 4

            df_final.loc[index_position, k] = val

print('\nFinal dataframe -')
df_final = df_final.reindex([0, 1, 2, 3, 4])
df_final.index = ['1_clients', '2_clients', '3_clients', '4_clients', '5_clients']

print(df_final)