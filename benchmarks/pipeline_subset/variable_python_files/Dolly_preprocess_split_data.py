# %%

import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import re
import cv2

def preprocess_split_data():
    # %%

    load_dotenv()

    # %%

    DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH")

    # %%

    plant_df_split = pd.read_csv(f'{DATA_FOLDER_PATH}/plant_data_split.csv')
    # %%

    growth_plant_df_split = pd.read_csv(f'{DATA_FOLDER_PATH}/growth_chamber_plant_data_split.csv')
    # %%

    plant_df_split = plant_df_split[["Trial", "Dataset", "Genotype", "Condition", "Original image path", "Masked image path", "Split masked image path"]]
    # %%

    growth_plant_df_split = growth_plant_df_split[["Trial", "Dataset", "Genotype", "Condition", "Original image path", "Masked image path", "Split masked image path"]]

    # %%

    growth_plant_df_split.dropna(inplace=True)

    # %%

    plant_df_split.dropna(inplace=True)
    # %%

    plant_df_split_master = pd.concat([plant_df_split, growth_plant_df_split])

    # %%

    plant_df_split_master['Label Category'] = pd.Categorical(plant_df_split_master['Condition'])
    plant_df_split_master['Label'] = plant_df_split_master['Label Category'].cat.codes

    # %%

    plant_df_split_master = plant_df_split_master.reset_index()

    # %%

    plant_split_master_file_name = "plant_data_split_master.csv"
    plant_split_master_file_path = os.path.join(DATA_FOLDER_PATH, plant_split_master_file_name)
    plant_df_split_master.to_csv(plant_split_master_file_path)
# %%

def condition_to_label(df):
    df['Label Category'] = pd.Categorical(df['Condition'])
    df['Label'] = df['Label Category'].cat.codes
    return df
