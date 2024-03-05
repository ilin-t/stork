import pandas as pd
import glob
import argparse

from preprocess import preprocess_sample
from feature_engineering import abun_per_tempbin

TRAIN_FILES = glob.glob("data/train_features/*.csv")
TRAIN_LABELS = pd.read_csv("data/train_labels.csv")
VALID_FILES = glob.glob("data/val_features/*.csv")
TEST_FILES = glob.glob("data/test_features/*.csv")

parser = argparse.ArgumentParser(description="Feature Engineering Pipeline")
parser.add_argument("-f",
                    "--feature",
                    help="name of feature", type=str)
parser.add_argument("-i",
                    "--interval",
                    help="temperature interval", type=int)
parser.add_argument("-s",
                    "--save",
                    help="enter no or the location to save the model", default='no', type=str)

args = parser.parse_args()


def generate_data(train: bool, feature: str) -> pd.DataFrame:
    """ 
    Generates a training dataset 
    
    Args:
        train: True if training set, False if testing set
        feature: string name of the feature to extract

    Returns:
        the dataset
    """

    train_features_dict = {}
    if train:
        files = TRAIN_FILES + VALID_FILES
    else:
        files = VALID_FILES + TEST_FILES

    for filename in files:

        # Load training sample
        temp = pd.read_csv(filename)
        sample_id = filename.split("\\")[1].split(".")[0]

        # Preprocessing training sample
        train_sample_pp = preprocess_sample(temp)

        # Feature engineering
        train_sample_fe = abun_per_tempbin(train_sample_pp, feature, args.interval).reset_index(drop=True)
        train_features_dict[sample_id] = train_sample_fe

    train_features = pd.concat(
        train_features_dict, names=["sample_id", "dummy_index"]
    ).reset_index(level="dummy_index", drop=True)

    return train_features

if __name__ == "__main__":
    if args.feature == "max":
        train = generate_data(True, "max")
        test = generate_data(False, "max")
        train_extention = f"max{args.interval}_train.csv"
        test_extention = f"max{args.interval}_test.csv"
    elif args.feature == "mean":
        train = generate_data(True, "mean")
        test = generate_data(False, "mean")
        train_extention = f"mean{args.interval}_train.csv"
        test_extention = f"mean{args.interval}_test.csv"
    else:
        raise Exception("Not Implemented")

    if args.save != 'no':
        train.to_csv(f"{args.save}/{train_extention}")
        test.to_csv(f"{args.save}/{test_extention}")