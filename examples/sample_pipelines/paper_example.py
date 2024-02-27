import numpy as np
import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from io import StringIO

DATA_HOME = "/home/user/DS-project/data"
DATA_WEB = 'https://example.com/user/data'
train_data_1 = pd.read_csv(f'{DATA_HOME}/train_data1.csv')
response = requests.get(f'{DATA_WEB}/train_data2.json')
train_data_2 = pd.read_json(StringIO(response.text))
train_data_2['quantity'] = train_data_2['quantity'].apply(lambda x: np.log(x + 1))
train_data = pd.concat([train_data_1, train_data_2])
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('logreg', LogisticRegression())])
pipeline.fit(train_data[:, :-1], train_data[:, -1])
test_data = pd.read_csv(f'{DATA_HOME}/test_data.csv')
X_test = test_data.drop('target_column', axis=1)
y_test = test_data['target_column']
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)