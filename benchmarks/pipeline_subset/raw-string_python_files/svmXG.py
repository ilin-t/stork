# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 22:24:37 2023

@author: adrian
"""


import pandas as pd
import math
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, auc
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn import svm


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


s_v = svm.SVC(kernel='sigmoid', probability=True)
s_v.fit(X_train, y_train)
y_pred = s_v.predict(X_test)


sv_accuracy = accuracy_score(y_test, y_pred)
sv_precision = precision_score(y_test, y_pred)
sv_recall = recall_score (y_test, y_pred)

print(f'Accuracy: {sv_accuracy:.2f}')
print(f'Precision: {sv_precision:.2f}')
print(f'Recall: {sv_recall:.2f}')


y_pred_proba = s_v.predict_proba(X_test)[:,0]
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




















