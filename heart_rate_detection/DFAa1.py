import numpy as np
import pandas as pd
import glob
from scipy.signal import find_peaks
from scipy.interpolate import UnivariateSpline
import os

def calculate_dfa(Y, scale_range):
    F = []
    for scale in scale_range:
        segments = len(Y) // scale
        rms = []
        for i in range(segments):
            segment = Y[i*scale:(i+1)*scale]
            x = np.arange(scale)
            coeffs = np.polyfit(x, segment, 1)
            trend = np.polyval(coeffs, x)
            rms.append(np.sqrt(np.mean((segment - trend)**2)))
        F.append(np.sqrt(np.mean(np.array(rms)**2)))
    return F

def calculate_alpha1_over_windows(time_data, hr_data, interval=3):
    alphas = []
    times = []
    
    start_time = time_data[0]
    end_time = time_data[-1]

    current_time = start_time

    window_size = 60
    scale_range = range(4, window_size // 4)

    while current_time < end_time:
        next_time = current_time + interval
        mask = (time_data >= current_time) & (time_data < next_time)

        if np.any(mask):
            time_segment = time_data[mask]
            hr_segment = hr_data[mask]
            
            Y = np.cumsum(hr_segment - np.mean(hr_segment))
            F = calculate_dfa(Y, scale_range)
            log_scale = np.log(scale_range)
            log_F = np.log(F)
            alpha1, _ = np.polyfit(log_scale, log_F, 1)
            alphas.append(alpha1)
            times.append(current_time)
        
        current_time = next_time

    return alphas, times

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
            HR_signals = df['HR'].values
            time_data = df['TIME'].values
        
        # 计算每3秒的α1
        alphas,times = calculate_alpha1_over_windows(time_data,HR_signals,3)

        output_file = os.path.join("/root/AIOT/project/heart_rate_detection/processed_data", f"processed_temp_{index}.csv")

        df = pd.DataFrame({'Time(s)': times,'alphas':alphas})
        df.to_csv(output_file,index = False)
                  
        print(f"Successfully saved file {index}")

        index += 1

    print("Success in all!")
