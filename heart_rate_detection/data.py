import pandas as pd
import os

file_root = "/root/AIOT/project/heart_rate_detection/processed_data"

for index in range(1,13):

    file1 = os.path.join(file_root,f"processed_{index}.csv")
    file2 = os.path.join(file_root,f"processed_temp_{index}.csv")
    file3 = os.path.join(file_root,f"processed_temp2_{index}.csv")

    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    df3 = pd.read_csv(file3)

    df2 = df2.drop(columns=['Time(s)'])
    df3 = df3.drop(columns=['Time(s)'])

    combined_df = pd.concat([df1, df2, df3], axis=1)

    output_file = os.path.join("/root/AIOT/project/heart_rate_detection/processed_final_data",f"final_{index}.csv")

    combined_df.to_csv(output_file, index=False)

    print(f"Successfully saved file {index}")

print("Success in all!")
