# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 23:57:56 2023

@author: adrian
"""

import pandas as pd
import math

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay, auc
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from scipy.stats import randint
from sklearn.preprocessing import LabelEncoder
from sklearn import metrics
import matplotlib.pyplot as plt
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

param_dist = {'n_estimators': randint(100,500),
              'max_depth': randint(1,20)}






rf = RandomForestClassifier()

rand_search = RandomizedSearchCV(rf, 
                                 param_distributions = param_dist, 
                                 n_iter=20, 
                                 cv=5)

rand_search.fit(X_train, y_train)

# Create a variable for the best model
best_rf = rand_search.best_estimator_



y_pred = best_rf.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)


cm = confusion_matrix(y_test, y_pred)

ConfusionMatrixDisplay(confusion_matrix=cm).plot();

plt.show()

precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)


print("Precision:", precision)
print("Recall:", recall)

#Creats data for a bar chat showing feature importances from the model and feature names from the training data
feature_importances = pd.Series(best_rf.feature_importances_, index=X_train.columns).sort_values(ascending=False)

# Plotthe bar chart
feature_importances.plot.bar();
plt.show()


y_pred_proba = best_rf.predict_proba(X_test)[:,1]
fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr,tpr)


plt.figure(figsize=(8,6))
plt.plot(fpr, tpr, color ='darkorange', lw=2, label = 'ROC curve (area = %0.2f)' % roc_auc)


plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc='lower right')
plt.show()




















