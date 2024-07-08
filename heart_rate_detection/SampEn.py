import numpy as np
import pandas as pd
import glob
from scipy.signal import find_peaks
from scipy.interpolate import UnivariateSpline
import os

def embedding(x, m):
    N = len(x)
    return np.array([x[i:i+m] for i in range(N-m+1)])

def _phi(data,m):
    A = embedding(data, m)
    C = np.zeros(A.shape[0])
    for i in range(A.shape[0]):
        C[i] = np.sum(np.max(np.abs(A[i] - A), axis=1) < r) / (A.shape[0] - 1)
    return np.mean(C)

def sample_entropy(hr_data,time_data, m, r,interval=3):
    SampEn = []
    times = []

    start_time = time_data[0]
    end_time = time_data[-1]

    current_time = start_time

    while current_time <end_time:
        next_time = current_time +interval
        mask = (time_data >= current_time ) & (time_data <next_time)

        if np.any(mask):
            time_segment = time_data[mask]
            hr_segment = hr_data[mask]

            phi_m = _phi(hr_segment,m)
            phi_m1 = _phi(hr_segment,m + 1)

            if phi_m > 0:
                SampEn.append(-np.log(phi_m1 / phi_m))
            else:
                SampEn.append(nan)

            times.append(current_time)

        current_time = next_time
    
    return SampEn,times

if __name__ == "__main__":
    # 使用你自己的路径
    directory_path = "/root/AIOT/project/heart_rate_detection/data"
    # 读取所有 CSV 文件
    csv_files = glob.glob(os.path.join(directory_path, '*.csv'))

    # 处理读取的所有文件
    index = 1
    for file in csv_files:
        df = pd.read_csv(file)
        df = df[10000:]
        df['HR'] = df['HR'].replace(0,np.nan)
        df = df.dropna(subset=['HR'])
        if 'HR' in df.columns and 'TIME' in df.columns:
            hr_signals = df['HR'].values
            time_data = df['TIME'].values

            m = 2
            r = 0.2 * np.std(hr_signals)  # 使用 HR 数据的标准差来设定 r

            sampen,times = sample_entropy(hr_signals,time_data, m,r,3)

            output_file = os.path.join("/root/AIOT/project/heart_rate_detection/processed_data", f"processed_temp2_{index}.csv")

            df = pd.DataFrame({'Time(s)': times,'SampEn':sampen})
            df.to_csv(output_file,index = False)
            
            print(f"Successfully saved file {index}")

            index += 1
            
    print("Success in all!")