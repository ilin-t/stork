# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 22:24:37 2023

@author: adrian
"""

import pandas as pd
import math
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import tensorflow as tf
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

nn = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(3,)),  # Input layer with 4 features
    tf.keras.layers.Dense(128, activation='relu'),  # Hidden layer with 64 units and ReLU activation
    tf.keras.layers.Dense(64, activation='relu'),  # Hidden layer with 64 units and ReLU activation
    tf.keras.layers.Dense(32, activation='relu'),  # Hidden layer with 64 units and ReLU activation
    tf.keras.layers.Dense(1, activation='sigmoid')  # Output layer with 3 units (one for each class) and softmax activation
])


nn.compile(optimizer='adam', 
              loss='binary_crossentropy',  # Use this loss for multi-class classification
              metrics=['accuracy'])  # Track accuracy as a metric

history = nn.fit(X_train, y_train, epochs=5000, validation_split=0.2, verbose=2)




test_loss, test_accuracy = nn.evaluate(X_test, y_test, verbose=0)
print(f'Test accuracy: {test_accuracy:.4f}')


nn_pred = nn.predict(X_test)



nn_pred = nn.predict(X_test, batch_size=64, verbose=1)
y_pred_bool = np.argmax(nn_pred, axis=1)

print(classification_report(y_test, y_pred_bool))

















