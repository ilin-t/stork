import pandas as pd
import numpy as np
import pickle
import argparse

parser = argparse.ArgumentParser(description="Feature Engineering Pipeline")
parser.add_argument("-m",
                    "--model_path",
                    help="path to pickle object of model", type=str)
parser.add_argument("-f",
                    "--feature",
                    help="name of feature", type=str)
parser.add_argument("-s",
                    "--save",
                    help="enter no or the location to save the model", default='no', type=str)

args = parser.parse_args()


def predict(test_df: pd.DataFrame, path: str):
    """
    Creates submission dataframe 

    Args:
        test_df: input features
        path: string file path to models

    Returns:
        the submission dataframe
    """

    models = load_object(path)
    sub = pd.read_csv("data/submission_format.csv", index_col="sample_id")

    for k in models.keys():
        preds = list()
        for model in models[k]:
            preds.append( model.predict_proba(test_df)[:, 1] )
        sub[k] = np.mean(preds, axis=0)

    return sub

def load_object(file_path):
    """ 
    Loads a pkl object 

    Args: 
        file_path: string path to the file

    Returns:
        the object
    """

    file = open(file_path, 'rb')
    model = pickle.load(file)
    file.close()
    return model

if __name__ == "__main__":
    test_df = pd.read_csv(f"data/stage2_features/{args.feature}_test.csv", header=[0], low_memory=False)
    test_df.columns = test_df.iloc[0]
    test_df = test_df.drop([0,1]).set_index('temp_bin', drop=True)
    sub = predict(np.array(test_df), args.model_path)
    sub.to_csv(args.save)    

