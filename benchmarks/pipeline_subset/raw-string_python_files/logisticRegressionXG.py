# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 19:51:08 2023

@author: adrian
"""
import pandas as pd
import math
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, auc
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt

#Function to help with maths calculations
def square(num):
    return num * num

#Creation of shots dataframe with the appropriate calculations
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

"""
#Uncomment to look at dataframe created

print(RM_df_2)
"""

X = RM_df_2[['ShotDistance', 'ShotAngle', 'shotType']]


y = RM_df_2['Goal']


X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2, random_state=42)


#Logistic Regression Calculations - Shot Distance feature

lr_1 = LogisticRegression()
lr_1.fit(X_train[['ShotDistance']], y_train)

x1_values = np.linspace(X_test['ShotDistance'].min() - 1, X_test['ShotDistance'].max() + 1, 2000)
probs_feature1 = lr_1.predict_proba(x1_values.reshape(-1, 1))[:, 1]

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(x1_values, probs_feature1, marker='o', linestyle='-')
plt.scatter(X_test['ShotDistance'], y_test, color='red', marker='x', label='Test Data')
plt.xlabel('ShotDistance')
plt.ylabel('Probability of Goal')
plt.title('Logistic Regression Curve for ShotDistance')
plt.legend()

coef_ShotDistance = lr_1.coef_[0][0]
coef_D_Intercept = lr_1.intercept_[0]

with open ("shotDistanceModel.txt", "w") as file:
    file.write("coef_ShotDistance: " + str(-1* coef_ShotDistance))
    file.write("\ncoef_D_Intercept: " + str(-1*coef_D_Intercept))
    



#Logistic Regression Calculations - Shot Angle feature

lr_2 = LogisticRegression()
lr_2.fit(X_train[['ShotAngle']], y_train)

x2_values = np.linspace(X_test['ShotAngle'].min() - 1, X_test['ShotAngle'].max() + 1, 2000)
probs_feature2 = lr_2.predict_proba(x2_values.reshape(-1, 1))[:, 1]

plt.subplot(1, 2, 2)
plt.plot(x2_values, probs_feature2, marker='o', linestyle='-')
plt.scatter(X_test['ShotAngle'], y_test, color='green', marker='s', label='Test Data')
plt.xlabel('ShotAngle')
plt.ylabel('Probability of Goal')
plt.title('Logistic Regression Curve for ShotAngle')
plt.legend()

coef_ShotAngle = lr_2.coef_[0][0]
coef_SA_intercept = lr_2.intercept_[0]

with open ("shotAngleModel.txt", "w") as file:
    file.write("coef_ShotAngle: " + str(-1* coef_ShotAngle))
    file.write("\ncoef_SA_intercept: " + str(-1*coef_SA_intercept))




print(f"Equation for Logistic Regression Curve of Shot Distance Feature: P(Y=1) = 1 / (1 + e^({-coef_D_Intercept} + {coef_ShotDistance} * X))")
print(f"Equation for Logistic Regression Curve of Shot Angle Feature: P(Y=1) = 1 / (1 + e^({-coef_SA_intercept} + {coef_ShotAngle} * X))")

lr_combined = LogisticRegression()
lr_combined.fit(X_train[['ShotDistance', 'ShotAngle', 'shotType']], y_train)

y_pred = lr_combined.predict(X_test)



combined_feature1 = lr_combined.coef_[0][0]
combined_feature2 = lr_combined.coef_[0][1]
intercept = lr_combined.intercept_[0]
print(f"Equation for Logistic Regression Curve with Both Features: P(Y=1) = 1 / (1 + e^({-intercept} + {combined_feature1} * Feature1 + {combined_feature2} * Feature2))")


accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
print("\n")
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)


"""
plt.tight_layout()
plt.show()
"""
y_pred_proba = lr_combined.predict_proba(X_test)[:,1]
fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred_proba)
roc_auc = auc (fpr, tpr)




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


























