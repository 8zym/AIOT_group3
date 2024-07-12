import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

# 设置光照强度范围
illumination_levels = np.linspace(300, 6000, 100)  # 从300到6000，生成100个点

# 定义分段函数
def fatigue_score(illumination):
    if illumination < 1500:
        return 5 - 0.001 * (illumination - 300)  # 平缓下降函数
    else:
        a = 0.0000005  # 调整曲线的开口方向和宽度
        h = 1500
        k = 3
        return a * (illumination - h)**2 + k

# 计算疲劳评分
fatigue_scores = np.array([fatigue_score(x) for x in illumination_levels])

# 添加一些噪声
np.random.seed(42)
noise = np.random.normal(0, 0.5, len(fatigue_scores))
fatigue_scores = fatigue_scores + noise

# 保证疲劳评分在 0 和 10 之间
fatigue_scores = np.clip(fatigue_scores, 0, 10)

# 创建 DataFrame
data = {
    "Illumination (lx)": illumination_levels,
    "Fatigue Score": fatigue_scores
}
df = pd.DataFrame(data)

# 保存为CSV文件
df.to_csv("segmented_light_fatigue_data.csv", index=False)
print("Data saved to 'segmented_light_fatigue_data.csv'")

# 可视化
plt.scatter(illumination_levels, fatigue_scores, color='blue', label='Fatigue Score')
plt.xlabel("Illumination (lx)")
plt.ylabel("Fatigue Score")
plt.title("Illumination vs. Fatigue Score")
plt.legend()
plt.show()

