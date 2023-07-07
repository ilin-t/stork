import numpy as np
import pandas as pd
import examples.db_playgrounds.postgresqlPlayground as pp

path = "data"

from_path = open("data/random.txt").read()
from_csv = pd.read_csv("data/random.csv")
auto_generate = np.zeros_like(from_csv)
# Add double output i.e., train/test split from a single file

postgres = pp.PostgresqlPlayground()
postgres.connect()


# print(from_path)
# print(from_csv)
# print(auto_generate)


