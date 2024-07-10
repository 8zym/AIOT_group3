import numpy as np
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score
from sklearn.neighbors import NearestNeighbors

# 读取数据
file_root = "/root/AIOT/project/heart_rate_detection/processed_final_data/final_1.csv"
df = pd.read_csv(file_root)

# 选择要用于降维和聚类的特征
features = ['LF Power', 'HF Power', 'alphas', 'SampEn']
X = df[features].values

# 标准化数据
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 创建PCA对象并指定要保留的主成分数目
pca = PCA(n_components=2)

# 使用PCA对数据进行降维
X_pca = pca.fit_transform(X_scaled)

# 打印降维后的数据
print("降维后的数据：")
print(X_pca)

# 寻找最佳eps值
neighbors = NearestNeighbors(n_neighbors=5)
neighbors_fit = neighbors.fit(X_pca)
distances, indices = neighbors_fit.kneighbors(X_pca)

# 计算每个点到其第5个最近邻的距离，并对距离进行排序
distances = np.sort(distances[:, 4], axis=0)
plt.plot(distances)
plt.title("k-最近邻距离曲线")
plt.xlabel("数据点索引")
plt.ylabel("第5个最近邻距离")
plt.show()

# 训练DBSCAN模型，尝试调整eps和min_samples参数
dbscan = DBSCAN(eps=0.1, min_samples=10)  # 根据k-最近邻距离曲线调整参数
dbscan.fit(X_pca)

# 获取聚类结果
labels = dbscan.labels_
df['Cluster'] = labels

# 打印每个类的中心，观察特征以标注类别
# DBSCAN没有明确的簇中心，这部分可以省略或替换为其他逻辑

# 假设Cluster -1是噪声，其他簇根据实际情况进行标注
df['Fatigue_Label'] = df['Cluster'].apply(lambda x: 'non-fatigue-driving' if x == 0 else ('fatigue-driving' if x == 1 else 'noise'))

# 评估聚类效果
# DBSCAN可能会产生噪声点（标签为-1），需要在计算轮廓分数时排除这些点
core_samples_mask = labels != -1
unique_labels = set(labels[core_samples_mask])
if len(unique_labels) > 1:
    sil_score = silhouette_score(X_pca[core_samples_mask], labels[core_samples_mask])
    print(f"Silhouette Score: {sil_score}")
else:
    print("无法计算轮廓分数，因为只有一个有效簇。")

# 如果有真实标签
if 'True_Label' in df.columns:
    true_labels = df['True_Label']
    ari_score = adjusted_rand_score(true_labels, labels)
    nmi_score = normalized_mutual_info_score(true_labels, labels)
    print(f"Adjusted Rand Index (ARI): {ari_score}")
    print(f"Normalized Mutual Information (NMI): {nmi_score}")

# 保存DBSCAN模型
joblib.dump(dbscan, 'dbscan_model_pca.pkl')

# 可视化聚类结果
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='prism')
plt.title('DBSCAN聚类结果')
plt.xlabel('主成分1')
plt.ylabel('主成分2')
plt.show()
