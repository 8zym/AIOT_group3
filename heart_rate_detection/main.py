import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score
import matplotlib.pyplot as plt

file_root = "/root/AIOT/project/heart_rate_detection/processed_final_data/final_1.csv"
data = pd.read_csv(file_root)


# 选择你认为重要的特征
features = [ 'LF_div_HF', 'alphas']

# 提取特征
X = data[features]

# 标准化数据
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 训练KMeans模型
kmeans = KMeans(n_clusters=2, random_state=0, n_init=10)  # 明确指定n_init以避免警告
kmeans.fit(X_scaled)

# 获取聚类结果
labels = kmeans.labels_
data['Cluster'] = labels

# 打印每个类的中心，观察特征以标注类别
centers = kmeans.cluster_centers_
print("Cluster Centers:")
print(scaler.inverse_transform(centers))

# 假设Cluster 0是非疲劳驾驶，Cluster 1是疲劳驾驶
data['Fatigue_Label'] = data['Cluster'].apply(lambda x: 'non-fatigue-driving' if x == 0 else 'fatigue-driving')

# 评估聚类效果
sil_score = silhouette_score(X_scaled, labels)
print(f"Silhouette Score: {sil_score}")

# 如果有真实标签
if 'True_Label' in data.columns:
    true_labels = data['True_Label']
    ari_score = adjusted_rand_score(true_labels, labels)
    nmi_score = normalized_mutual_info_score(true_labels, labels)
    print(f"Adjusted Rand Index (ARI): {ari_score}")
    print(f"Normalized Mutual Information (NMI): {nmi_score}")

joblib.dump(kmeans, 'kmeans_model.pkl')
