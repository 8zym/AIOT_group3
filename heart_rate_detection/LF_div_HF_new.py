import numpy as np
import pandas as pd
import glob
from scipy.signal import find_peaks
from scipy.interpolate import UnivariateSpline
import os
from scipy.signal import welch

def save_lf_hf_intervals(lf_norm, hf_norm, output_file):
    df = pd.DataFrame({'LF_norm': lf_norm, 'HF_norm': hf_norm})
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    # 使用你自己的路径
    directory_path = "/root/AIOT/project/heart_rate_detection/data"
    # 读取所有 CSV 文件
    csv_files = glob.glob(os.path.join(directory_path, '*.csv')) 

    index = 1   

    for file in csv_files:
        df = pd.read_csv(file)

        if 'HR' in df.columns and 'TIME' in df.columns:
            time_data = df['TIME'].values
            heart_rate_data = df['HR'].values

        segment_length = 1000
        overlap = 0

        lf_norms = []
        hf_norms = []

        fs = 1
        lf_band = (0.04, 0.15)
        hf_band = (0.15, 0.4)

        for start in range(0, len(heart_rate_data) - segment_length + 1, segment_length - overlap):
            segment = heart_rate_data[start:start + segment_length]
            f, pxx = welch(segment, fs, nperseg=len(segment))

            lf_mask = (f >= lf_band[0]) & (f <= lf_band[1])
            hf_mask = (f >= hf_band[0]) & (f <= hf_band[1])

            lf_power = np.trapz(pxx[lf_mask], f[lf_mask])
            hf_power = np.trapz(pxx[hf_mask], f[hf_mask])
            total_power = lf_power + hf_power

            lf_norm = lf_power / total_power if total_power != 0 else 0
            hf_norm = hf_power / total_power if total_power != 0 else 0

            lf_norms.append(lf_norm)
            hf_norms.append(hf_norm)

        output_file = os.path.join("/root/AIOT/project/heart_rate_detection/processed_data", f"processed_temp_{index}.csv")
            
        save_lf_hf_intervals(lf_norms, hf_norms, output_file)
        print(f"Successfully saved file {index}")

        index += 1

    print("Success in all!")
