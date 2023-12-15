import numpy as np
import pandas as pd
import examples.db_playgrounds.postgresqlPlayground as pp

def test_db_playground():
    a = pp.db_playground()


from_path = open("data/random.txt").read()
from_csv = pd.read_csv("data/random.csv")
auto_generate = np.zeros_like(from_csv)

postgres = pp.PostgresqlPlayground()
postgres.connect()

def main():
    c = test_db_playground()
    print("Defined main method")

if __name__ == '__main__':
    path = "data"
    main()


# print(from_path)
# print(from_csv)
# print(auto_generate)


