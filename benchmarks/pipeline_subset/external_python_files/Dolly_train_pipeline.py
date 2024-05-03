import pandas as pd
import numpy as np
from collections import defaultdict
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
import pickle
import argparse

from models import get_model

TRAIN_LABELS = pd.read_csv("data/train_labels.csv", index_col="sample_id")
VALID_LABELS = pd.read_csv("data/val_labels.csv", index_col="sample_id") # stage 2
LABELS = pd.concat([TRAIN_LABELS, VALID_LABELS]) # stage 2

parser = argparse.ArgumentParser(description="Feature Engineering Pipeline")
parser.add_argument("-m",
                    "--model",
                    help="name of model", type=str)
parser.add_argument("-f",
                    "--feature",
                    help="name of feature", type=str)
parser.add_argument("-s",
                    "--save",
                    help="enter no or the location to save the model", default='no', type=str)

args = parser.parse_args()

def train(train_df: pd.DataFrame, model_name: str, path: str) -> pd.DataFrame:
    """
    Trains the model

    Args:
        train_df: the training data
        model_name: string name of the model
        path: save path
    """

    model_dict = defaultdict(list)
    mskf = MultilabelStratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    for train_index, _ in mskf.split(train_df.values, LABELS):
        X_train = train_df.values[train_index]
        y_train = LABELS.values[train_index]
        y_train = pd.DataFrame(y_train, columns=LABELS.columns)

        for col in LABELS.columns:
            y_train_col = y_train[col]
            model = get_model(model_name)
            model_dict[col].append( model.fit(X_train, y_train_col) )

    pickle.dump(model_dict, open(path, 'wb'))

if __name__ == "__main__":
    train_df = pd.read_csv(f"data/savgol_features/{args.feature}_train.csv", header=[0], low_memory=False)
    train_df.columns = train_df.iloc[0]
    train_df = train_df.drop([0,1]).set_index('temp_bin', drop=True)

    train(train_df, args.model, args.save)