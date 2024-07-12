import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import joblib

# 加载数据集
df = pd.read_csv("segmented_light_fatigue_data.csv")
# 特征和标签
X = df[["Illumination (lx)"]]
y = df["Fatigue Score"]

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练回归模型
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 在测试集上进行预测
y_pred = model.predict(X_test)

# 评估模型性能
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print("Mean Squared Error:", mse)
print("R-squared:", r2)

# 可视化预测结果
plt.scatter(X_test.values.flatten(), y_test, color='blue', label='Actual Fatigue Score')
plt.scatter(X_test.values.flatten(), y_pred, color='red', label='Predicted Fatigue Score')
plt.xlabel("Illumination (lx)")
plt.ylabel("Fatigue Score")
plt.title("Actual vs. Predicted Fatigue Score")
plt.legend()
plt.show()

# 保存模型
joblib.dump(model, 'fatigue_regression_model.pkl')
print("Model saved successfully.")


