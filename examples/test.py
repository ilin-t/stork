import numpy as np
import pandas as pd


path = "data"

from_path = open(path + "/random.txt").read()
from_csv = pd.read_csv(path + "/random.csv")
auto_generate = np.zeros_like(from_csv)
# Add double output i.e., train/test split from a single file

print(from_path)
print(from_csv)
print(auto_generate)


