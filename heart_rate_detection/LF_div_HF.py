import numpy as np
import pandas as pd
import glob
from scipy.signal import find_peaks, welch
import os

def calculate_rr_intervals(hr_data):
    rr_intervals = []
    rr_intervals = 60 / hr_data
    return rr_intervals

def calculate_lf_hf(rr_intervals, sampling_rate):
    f, pxx = welch(rr_intervals, fs=sampling_rate, nperseg=len(rr_intervals))
    lf_band = (0.04, 0.15)
    hf_band = (0.15, 0.4)
    
    lf = np.trapz([pxx[i] for i in range(len(f)) if lf_band[0] <= f[i] <= lf_band[1]], 
                  [f[i] for i in range(len(f)) if lf_band[0] <= f[i] <= lf_band[1]])
    hf = np.trapz([pxx[i] for i in range(len(f)) if hf_band[0] <= f[i] <= hf_band[1]], 
                  [f[i] for i in range(len(f)) if hf_band[0] <= f[i] <= hf_band[1]])
    
    return lf, hf

def calculate_mean_rr_intervals_over_intervals(rr_intervals, rr_times, interval=3):
    mean_rr_intervals = []
    mean_rr_times = []
    lf_powers = []
    hf_powers = []
    lf_div_hf = []

    rr_times = np.array(rr_times)  # Ensure rr_times is a numpy array
    start_time = rr_times[0]
    end_time = rr_times[-1]

    current_time = start_time
    while current_time < end_time:
        next_time = current_time + interval
        mask = (rr_times >= current_time) & (rr_times < next_time)

        if np.any(mask):
            window_intervals = rr_intervals[mask]
            mean_rr_intervals.append(np.mean(window_intervals))
            mean_rr_times.append(current_time)
            if len(window_intervals) > 1:  # Need at least 2 intervals to calculate frequency components
                lf, hf = calculate_lf_hf(window_intervals, 1/np.mean(window_intervals))
                lf_powers.append(lf)
                hf_powers.append(hf)
                lf_div_hf.append(lf/hf)
            else:
                lf_powers.append(np.nan)
                hf_powers.append(np.nan)
                lf_div_hf.append(np.nan)
        else:
            mean_rr_intervals.append(np.nan)
            mean_rr_times.append(current_time)
            lf_powers.append(np.nan)
            hf_powers.append(np.nan)
            lf_div_hf.append(np.nan)

        current_time = next_time

    return mean_rr_intervals, mean_rr_times, lf_powers, hf_powers,lf_div_hf

def save_mean_rr_intervals(mean_rr_intervals, mean_rr_times, lf_powers, hf_powers, lf_div_hf,output_file):
    df = pd.DataFrame({'Time(s)': mean_rr_times, 
                       'Mean RR Interval (s)': mean_rr_intervals, 
                       'LF Power': lf_powers, 
                       'HF Power': hf_powers,
                       'LF_div_HF':lf_div_hf})
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    directory_path = "/root/AIOT/project/heart_rate_detection/data"
    csv_files = glob.glob(os.path.join(directory_path, '*.csv'))

    index = 1
    for file in csv_files:
        df = pd.read_csv(file)
        df = df[10000:]
        df['HR'] = df['HR'].replace(0,np.nan)
        df = df.dropna(subset=['HR'])
        hr_signals = df['HR']
        time_data = df['TIME']

        rr_intervals = calculate_rr_intervals(hr_signals)
        
        mean_rr_intervals, mean_rr_times, lf_powers, hf_powers,lf_div_hf = calculate_mean_rr_intervals_over_intervals(rr_intervals, time_data, interval=3)
        
        output_file = os.path.join("/root/AIOT/project/heart_rate_detection/processed_data", f"processed_{index}.csv")
        save_mean_rr_intervals(mean_rr_intervals, mean_rr_times, lf_powers, hf_powers,lf_div_hf, output_file)
        
        print(f"Successfully saved file {index}")
        index += 1

    print("Success in all!")
