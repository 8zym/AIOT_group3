import joblib
import pandas as pd

# 加载保存的模型
model = joblib.load('fatigue_detection_model.pkl')
print("Model loaded successfully.")

# 定义预测函数
def predict_fatigue(temperature, humidity):
    # 创建一个包含输入数据的新样本
    sample = pd.DataFrame({'Temperature': [temperature], 'Humidity': [humidity]})
    
    # 使用模型进行预测
    prediction = model.predict(sample)
    
    return prediction[0]

# 示例预测
temperature = 10   # 输入的温度值
humidity = 100    # 输入的湿度值
fatigue_status = predict_fatigue(temperature, humidity)
print("驾驶员驾驶环境预测结果:", fatigue_status)
