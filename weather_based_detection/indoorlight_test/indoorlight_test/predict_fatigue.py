import numpy as np
import joblib

# 加载已保存的模型
model = joblib.load('fatigue_regression_model.pkl')

# 定义预测函数
def predict_fatigue_score(illumination):
    sample_illumination = np.array([[illumination]])  # 输入光照强度
    predicted_fatigue_score = model.predict(sample_illumination)
    return predicted_fatigue_score[0]

if __name__ == "__main__":
    # 示例光照强度
    illumination_value = 1500
    predicted_score = predict_fatigue_score(illumination_value)
    print(f"Predicted fatigue score for {illumination_value} lx: {predicted_score}")
