import numpy as np
import pandas as pd
import glob
from scipy.signal import find_peaks
from scipy.interpolate import UnivariateSpline
import os

def detect_r_peaks(ecg_signals, sampling_rate):
    peaks, _ = find_peaks(ecg_signals, distance=int(sampling_rate * 0.6))
    return peaks

def calculate_rr_intervals(peaks, time_data):
    rr_intervals = np.diff(time_data[peaks])
    return rr_intervals, time_data[peaks][1:]

def calculate_mean_rr_intervals_over_intervals(rr_intervals, rr_times, interval=3):
    mean_rr_intervals = []
    mean_rr_times = []

    start_time = rr_times[0]
    end_time = rr_times[-1]

    current_time = start_time
    while current_time < end_time:
        next_time = current_time + interval
        mask = (rr_times >= current_time) & (rr_times < next_time)

        if np.any(mask):
            mean_rr_intervals.append(np.mean(rr_intervals[mask]))
            mean_rr_times.append(current_time)
        current_time = next_time
    
    return mean_rr_intervals, mean_rr_times

def save_mean_rr_intervals(mean_rr_intervals, mean_rr_times, output_file):
    df = pd.DataFrame({'Time(s)': mean_rr_times, 'Mean RR Interval (s)': mean_rr_intervals})
    df.to_csv(output_file, index=False)

def save_smooth_rr_interval(time,smooth_rr_intervals,output_file):
    df = pd.DataFrame({'Time(s)': time, 'Mean RR Interval (s)': smooth_rr_intervals})
    df.to_csv(output_file, index=False)

def spline_function(t):
    return spline(t)

if __name__ == "__main__":
    # 使用你自己的路径
    directory_path = "/root/AIOT/project/heart_rate_detection/data"
    # 读取所有 CSV 文件
    csv_files = glob.glob(os.path.join(directory_path, '*.csv'))

    # 处理读取的所有文件
    index = 1
    for file in csv_files:
        df = pd.read_csv(file)
        if 'ECG' in df.columns and 'TIME' in df.columns:
            ecg_signals = df['ECG'].values
            time_data = df['TIME'].values

            # 检测R波
            sampling_rate = 1000
            r_peaks = detect_r_peaks(ecg_signals, sampling_rate)

            rr_intervals, rr_times = calculate_rr_intervals(r_peaks, time_data)

#            df2 = pd.DataFrame({
#                'Time': rr_times,
#                'RR_Interval': rr_intervals
#            })

#            spline = UnivariateSpline(df2['Time'], df2['RR_Interval'], s=0.5)

            mean_rr_intervals, mean_rr_times = calculate_mean_rr_intervals_over_intervals(rr_intervals, rr_times, interval=3)

            output_file = os.path.join("/root/AIOT/project/heart_rate_detection/processed_data", f"processed_{index}.csv")

            save_mean_rr_intervals(mean_rr_intervals, mean_rr_times, output_file)
            
            print(f"Successfully saved file {index}")

            index += 1
            
    print("Success in all!")
