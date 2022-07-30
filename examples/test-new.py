import numpy as np
import pandas as pd
import sklearn


path = "data"

from_path = open("examples/random.txt").read()
from_csv = pd.read_csv("newnewn.csv")
auto_generate = np.zeros_like(from_csv)
# Add double output i.e., train/test split from a single file

print(from_path)
print(from_csv)
print(auto_generate)


