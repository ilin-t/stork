import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, LabelBinarizer
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, recall_score
import time
import openml
from pandas.api.types import is_numeric_dtype

dataset = openml.datasets.get_dataset(31)

df, y, _, _ = dataset.get_data(dataset_format="dataframe")

print(df.head(5))
print(df.dtypes)
print(list(df))
target = 'class'
training_features = list(df)
training_features.remove(target)
categorical_features = []
numerical_features = []


for x in training_features:
    if is_numeric_dtype(df[x].dtype):
        numerical_features.append(x)
    else:
        categorical_features.append(x)

print('found numerical features: ' + str(numerical_features))
print('found categorical features: ' + str(categorical_features))

numerical_transformer = Pipeline(steps=[('scaler', MinMaxScaler())])
categorical_transformer = Pipeline(steps=[('encoder', OneHotEncoder())])

preprocessor = ColumnTransformer(
                                transformers=[
                                                ('num', numerical_transformer, numerical_features),
                                                ('cat', categorical_transformer, categorical_features)
                                            ],
                                remainder='passthrough'
                                )

neural_network_pipeline = Pipeline(
                                    steps =[
                                                ('preprocessor', preprocessor),
                                                ('clf', MLPClassifier(
                                                                        activation= 'tanh',
                                                                        alpha= 0.5,
                                                                        hidden_layer_sizes= (50,),
                                                                        max_iter=10000
                                                                    )
                                                )
                                            ]
                                    )

X = df[training_features]
y = df[target]

lb = LabelBinarizer()
y = np.ravel(lb.fit_transform(y))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

tr_1nn = time.time()
trained_nn = neural_network_pipeline.fit(X_train, y_train)
tr_2nn = time.time() - tr_1nn

print(
        "Time to train nn: %0.3f"
        % tr_2nn
    )

t1nn = time.time()
y_pred = trained_nn.predict(X_test)
t2nn = time.time() - t1nn

print(
        "Recall score on test set: %0.3f"
        % recall_score(y_test, y_pred)
    )

print(
        "F1 score on test set: %0.3f"
        % f1_score(y_test, y_pred)
    )

