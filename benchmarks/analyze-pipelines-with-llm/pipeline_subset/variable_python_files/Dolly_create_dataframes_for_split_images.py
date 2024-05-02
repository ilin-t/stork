# %%

import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import re
import cv2

# %%

load_dotenv()

# %%

DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH")

# %%

plant_df = pd.read_csv(f'{DATA_FOLDER_PATH}/plant_data.csv')

# %%

plant_df['Split masked image path'] = ''

for index, row in plant_df.iterrows():
    trial = row['Trial']
    dataset = row['Dataset']
    plant_index = row['Tray Index']
    group_image_path = row['Masked image path']
    subfolder_pattern = re.compile(f'Data\/Trial_0{trial}\/Dataset_0{dataset}\/FishEyeMasked\/(.*)\-RGB.*')
    subfolder = re.search(subfolder_pattern, group_image_path).group(1)
    split_image_path = f'{DATA_FOLDER_PATH}/Separated_plants/Trial_0{trial}/Dataset_0{dataset}/Background_included/{subfolder}/plant_index_{plant_index}.png'

    img = cv2.imread(split_image_path)
    if img is None:
        plant_df.loc[index, 'Split masked image path'] = np.nan
    else:
        relative_path = os.path.relpath(split_image_path, DATA_FOLDER_PATH)
        plant_df.loc[index, 'Split masked image path'] = relative_path
# %%

plant_df.to_csv(f'{DATA_FOLDER_PATH}/plant_data_split.csv', index=False)

# %%
