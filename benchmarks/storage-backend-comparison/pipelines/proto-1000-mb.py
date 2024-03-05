import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

desired_size_bytes = 1000 * 1024 * 1024  # 1GB


num_rows = desired_size_bytes // (8 * 100)  # We use 64-bit float


column_names = [f"Column_{i}" for i in range(1, 101)]
data = np.random.random(size=(num_rows, 100))  # 100 columns for example

df = pd.DataFrame(data, columns=column_names)
df['Target'] = np.random.choice([0, 1], size=num_rows)

csv_file_path = '../generated-data/random_data_1000MB.csv'
df.to_csv(csv_file_path, index=False)

loaded_df=pd.read_csv('../generated-data/random_data_1000MB.csv', index_col=0)

X = loaded_df.drop('Target', axis=1)
y = loaded_df['Target']

X = df.drop('Target', axis=1)
y = df['Target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
logreg = LogisticRegression()
logreg.fit(X_train, y_train)
y_pred = logreg.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
