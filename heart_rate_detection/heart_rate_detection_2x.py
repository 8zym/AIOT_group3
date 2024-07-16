import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
import pymysql
import numpy as np
import pandas as pd
import glob
from sklearn.cluster import KMeans
from scipy.signal import find_peaks, welch
from scipy.interpolate import UnivariateSpline
import os
import time

def calculate_rr_intervals(hr_data):
    rr_intervals = []
    rr_intervals = [60 / hr for hr in hr_data]
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

# 连接到数据库
db = pymysql.connect(
    host='47.121.193.122',
    user='root',
    password='123456',
    database='emqx_data',  # 指定数据库
    cursorclass=pymysql.cursors.DictCursor
)

cursor = db.cursor()  # 创建一个指针

while True:

    query = 'SELECT * FROM heart_rate ORDER BY id DESC;'  # 替换为heart_rate数据库中的实际表名
    cursor.execute(query)
    # 获取查询结果
    results = cursor.fetchall()
    results = [row['heart_rate'] for row in results[0:30]]
    print(results)

    rr_intervals = calculate_rr_intervals(results)
    lf,hf = calculate_lf_hf(rr_intervals,1/np.mean(rr_intervals))
    lf_div_hf = lf/hf

    window_size = 30
    scale_range = range(4, window_size // 4)
    Y = np.cumsum(results - np.mean(results))
    F = calculate_dfa(Y,scale_range)
    log_scale = np.log(scale_range)
    log_F = np.log(F)
    alpha1, _ = np.polyfit(log_scale,log_F,1)


    # 加载模型
    kmeans = joblib.load('model/kmeans_model_all.pkl')

    # 选择与训练数据相同的特征
    new_data = pd.DataFrame({
        'LF Power': [lf],
        'LF_div_HF': [lf_div_hf],
        'alphas': [alpha1]
    })
    new_features =  ['LF_div_HF','alphas']
    X_new = new_data[new_features]

    # 标准化新数据，使用与训练数据相同的 scaler
    scaler = StandardScaler()
    X_new_scaled = scaler.fit_transform(X_new)  # 注意：在实际使用中应使用与训练相同的 scaler

    # 使用加载的模型进行预测
    print(X_new_scaled)
    predicted_labels = kmeans.predict(X_new_scaled)

    # 映射到具体标签
    label_mapping = {1: 'non-fatigue-driving', 0: 'fatigue-driving'}
    new_data['Predicted_Fatigue_Label'] = [label_mapping[label] for label in predicted_labels]

    # 打印预测结果
    print(new_data[['LF_div_HF', 'alphas', 'Predicted_Fatigue_Label']])

    time.sleep(5)

# 关闭游标和数据库连接
cursor.close()
db.close()
