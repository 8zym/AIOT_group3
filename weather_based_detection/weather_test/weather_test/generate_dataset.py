import numpy as np
import pandas as pd

# 设置随机种子以确保结果可复现
np.random.seed(42)

# 生成模拟数据
num_samples = 1000
temperature = np.random.uniform(15, 40, num_samples)  # 温度数据
humidity = np.random.uniform(20, 90, num_samples)     # 湿度数据

# 计算温湿指数
THI = temperature - (0.55 - 0.55 * (humidity / 100)) * (temperature - 14.4)

# 判断对疲劳的抵御值
resistance_values = []
for thi in THI:
    if 17 <= thi <= 25.4:
        resistance_values.append('不容易疲劳')
    elif 14 <= thi < 17 or 25.5 <= thi <= 27.5:
        resistance_values.append('较容易疲劳')
    elif thi < 14 or thi > 27.5:
        resistance_values.append('特别容易疲劳')
    else:
        resistance_values.append('未知')  # 处理异常情况

# 创建数据框
data = pd.DataFrame({
    'Temperature': temperature,
    'Humidity': humidity,
    'THI': THI,
    'Resistance_Value': resistance_values
})

# 保存数据集到 CSV 文件
data.to_csv('weather_data.csv', index=False)
print("Data saved to 'weather_data.csv'")