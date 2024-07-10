import numpy as np
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score

# 读取数据
file_root = "/root/AIOT/project/heart_rate_detection/processed_final_data/final_1.csv"
df = pd.read_csv(file_root)

# 选择要用于降维和聚类的特征
features = [ 'LF Power','LF_div_HF', 'alphas']
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

# 训练KMeans模型
kmeans = KMeans(n_clusters=2, random_state=0, n_init=10)  # 明确指定n_init以避免警告
kmeans.fit(X_pca)

# 获取聚类结果
labels = kmeans.labels_
df['Cluster'] = labels

# 打印每个类的中心，观察特征以标注类别
centers = kmeans.cluster_centers_
print("Cluster Centers:")
print(scaler.inverse_transform(pca.inverse_transform(centers)))

# 假设Cluster 0是非疲劳驾驶，Cluster 1是疲劳驾驶
df['Fatigue_Label'] = df['Cluster'].apply(lambda x: 'non-fatigue-driving' if x == 0 else 'fatigue-driving')

# 评估聚类效果
sil_score = silhouette_score(X_pca, labels)
print(f"Silhouette Score: {sil_score}")

# 如果有真实标签
if 'True_Label' in df.columns:
    true_labels = df['True_Label']
    ari_score = adjusted_rand_score(true_labels, labels)
    nmi_score = normalized_mutual_info_score(true_labels, labels)
    print(f"Adjusted Rand Index (ARI): {ari_score}")
    print(f"Normalized Mutual Information (NMI): {nmi_score}")

# 保存KMeans模型
joblib.dump(kmeans, 'kmeans_model_pca.pkl')

# 可视化聚类结果
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='prism')
plt.title('KMeans聚类结果')
plt.xlabel('主成分1')
plt.ylabel('主成分2')
plt.show()
