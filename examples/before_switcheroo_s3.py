import pandas as pd
import numpy as np
import sklearn

from pandas.core.dtypes.common import is_numeric_dtype
from sklearn.compose import ColumnTransformer
from sklearn.metrics import recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, LabelBinarizer, MultiLabelBinarizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from scipy.io import arff

dataset = arff.loadarff("data/dataset_31_credit-g.arff")

df = pd.DataFrame(dataset[0])
print(df.head())
for column in df.columns:
    if not is_numeric_dtype(df[column].dtype):
        df[column] = df[column].apply(
            lambda x: x.decode("utf-8"))

print(df.head())

num_features = len(df.columns)
data = df.iloc[:, 0:num_features - 1]
labels = df["class"]

training_features = list(data)
numerical_features = []
categorical_features = []

for feature in training_features:
    if is_numeric_dtype(df[feature].dtype):
        numerical_features.append(feature)
    else:
        categorical_features.append(feature)

print('found numerical features: ' + str(numerical_features))
print('found categorical features: ' + str(categorical_features))

ct = ColumnTransformer(
    transformers=[
        ("numerical_transform", MinMaxScaler(), numerical_features),
        ("categorical_transform", OneHotEncoder(), categorical_features)],
    remainder='passthrough')

rf = Pipeline([
    ("feature_transformation", ct),
    ('random_forest_classifier', RandomForestClassifier(n_estimators=100))
])

# Binarize labels

print(labels.head())
lb = LabelBinarizer()
labels = np.ravel(lb.fit_transform(labels))

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.3, random_state=10)

# Train the algorithm
rf_model = rf.fit(X_train, y_train)

# Generate predictions
y_pred = rf_model.predict(X_test)

print(
    "Recall score on test set: %0.3f"
    % recall_score(y_test, y_pred)
)

print(
    "F1 score on test set: %0.3f"
    % f1_score(y_test, y_pred)
)
