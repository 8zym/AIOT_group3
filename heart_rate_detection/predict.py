import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

# 加载模型
kmeans = joblib.load('kmeans_model.pkl')

# 加载和预处理新数据
new_data_file = "/root/AIOT/project/heart_rate_detection/processed_final_data/final_2.csv"
new_data = pd.read_csv(new_data_file)

# 选择与训练数据相同的特征
new_features = ['LF_div_HF', 'alphas']
X_new = new_data[new_features]

# 标准化新数据，使用与训练数据相同的 scaler
scaler = StandardScaler()
X_new_scaled = scaler.fit_transform(X_new)  # 注意：在实际使用中应使用与训练相同的 scaler

# 使用加载的模型进行预测
predicted_labels = kmeans.predict(X_new_scaled)

# 映射到具体标签
label_mapping = {0: 'non-fatigue-driving', 1: 'fatigue-driving'}
new_data['Predicted_Fatigue_Label'] = [label_mapping[label] for label in predicted_labels]

# 打印预测结果
print(new_data[['LF_div_HF', 'alphas', 'Predicted_Fatigue_Label']])

# 保存预测结果
new_data.to_csv('/root/AIOT/project/heart_rate_detection/new_data_with_predictions.csv', index=False)
