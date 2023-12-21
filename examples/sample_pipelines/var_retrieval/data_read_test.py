import pandas as pd
import numpy as np
import argparse


def read_data(path):
    df7 = pd.read_csv(path)
    return df7


def main(args):
    user_root = "/home/ilint/"
    data_file = "/home/ilint/occurrences-2018.csv"
    data_folder="data/"

    df1 = pd.read_csv(f"{user_root}occurrences-2019.csv")
    df2 = pd.read_csv(user_root + "occurrences-2019.csv")
    df4 = pd.read_csv(user_root + data_folder + "occurrences-2019.csv")
    df6 = pd.read_csv(user_root + data_folder + data_file)
    df = read_data("/home/ilint/occurrences-2020.csv")
    df5 = pd.read_csv("{}/{}/{}".format(user_root, data_folder, "occurrences-2022.csv"))

    # user_root = args.root
    # data_path = args.data
    df3 = pd.read_csv(data_file)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('-r', '--root')
    args.add_argument('-d', '--data')

    args = args.parse_args()

    main(args)
