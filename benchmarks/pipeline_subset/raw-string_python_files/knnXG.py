# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 22:24:37 2023

@author: adrian
"""


import pandas as pd
import math
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, auc
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler



def square(num):
    return num * num


RM_df = pd.read_csv('RealMadrid2019shots.csv')
label_encoder = LabelEncoder()
RM_df['h_a'] = label_encoder.fit_transform(RM_df['h_a'])
RM_df['situation'] = label_encoder.fit_transform(RM_df['situation'])
RM_df['shotType'] = label_encoder.fit_transform(RM_df['shotType'])
RM_df['lastAction'] = label_encoder.fit_transform(RM_df['lastAction'])


X_meter = RM_df.X * 105
Y_meter = RM_df.Y * 68

GL_distance = square(105 - X_meter) + square(32.5 - Y_meter)

GL_distance = pd.DataFrame(GL_distance)

GL_distance = GL_distance.applymap(lambda x: x**0.5)

RM_df_2 =  RM_df.assign(ShotDistance=GL_distance)


N = 7.32 * (105 - X_meter)
D = square(105 - X_meter) + square(32.5- Y_meter) - square(7.32/2)

I = pd.DataFrame(N/D)

I = I.applymap(lambda x: math.atan(x))

S_Angle = I * 180/math.pi

RM_df_2 = RM_df_2.assign(ShotAngle=S_Angle)

X = RM_df_2[['ShotDistance', 'ShotAngle', 'shotType']]


y = RM_df_2['Goal']

print(X)
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


knn = KNeighborsClassifier(n_neighbors=8)
knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)

knn_accuracy = accuracy_score(y_test, y_pred)
knn_precision = precision_score(y_test, y_pred)
knn_recall = recall_score (y_test, y_pred)

print(f'Accuracy: {knn_accuracy:.2f}')
print(f'Precision: {knn_precision:.2f}')
print(f'Recall: {knn_recall:.2f}')


y_pred_proba = knn.predict_proba(X_test)[:,1]
fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)

plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc='lower right')
plt.show()






#Code Below plots a graph of accuracy against values of k from 1 to 31

"""
k_values = [i for i in range (1,31)]
scores = []

scaler = StandardScaler()
X = scaler.fit_transform(X)

for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    score = cross_val_score(knn, X, y, cv=5)
    scores.append(np.mean(score))


sns.lineplot(x = k_values, y = scores, marker = 'o')
plt.xlabel("K Values")
plt.ylabel("Accuracy Score")

"""








