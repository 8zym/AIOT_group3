import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import fcluster
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib

# 读取数据
file_root = "/root/AIOT/project/heart_rate_detection/processed_final_data/final_1.csv"
data = pd.read_csv(file_root)

# 选择要用于聚类的特征
features = [ 'LF Power', 'LF_div_HF', 'alphas']
X = data[features].values

# 标准化特征
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 使用层次聚类算法进行聚类
Z = linkage(X_scaled, method='ward')

# 绘制层次树（dendrogram）
plt.figure(figsize=(10, 5))
dendrogram(Z)
plt.title('层次树（Dendrogram）')
plt.xlabel('样本编号')
plt.ylabel('距离')
plt.show()

# 根据层次树进行截断，形成两个簇
num_clusters = 2
clusters = fcluster(Z, num_clusters, criterion='maxclust')

# 将聚类结果添加回原始数据
data['Cluster'] = clusters

# 添加疲劳标签
data['Fatigue_Label'] = data['Cluster'].apply(lambda x: 'non-fatigue-driving' if x == 1 else 'fatigue-driving')

# 计算轮廓分数
sil_score = silhouette_score(X_scaled, clusters)
print(f"Silhouette Score: {sil_score}")

# 保存模型
joblib.dump(Z, 'Hierarchical_model_pca.pkl')

# 打印前几行数据，验证结果
print(data.head())
