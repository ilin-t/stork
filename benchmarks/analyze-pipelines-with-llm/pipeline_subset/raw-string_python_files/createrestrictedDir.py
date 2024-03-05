import pandas as pd
import shutil
from tqdm import tqdm
import os

sourceFolder = "/Users/beppe2hd/Data/Microplastiche/imageswithR"
destForlder = "/Users/beppe2hd/Data/Microplastiche/HMPD-Gen/images"
df = pd.read_csv("./gt.csv")
dfP = pd.read_csv("./gtPossible.csv")

dfTot = pd.concat([df,dfP])
filesToCopy = dfTot.patchids.unique().tolist()

for i in tqdm(filesToCopy):
    source_R = os.path.join(sourceFolder, i  + "_R.bmp")
    source_A = os.path.join(sourceFolder, i  + "_A.bmp")
    source_P = os.path.join(sourceFolder, i  + "_P.bmp")
    dest_R = os.path.join(destForlder, i + "_R.bmp")
    dest_A = os.path.join(destForlder, i + "_A.bmp")
    dest_P = os.path.join(destForlder, i + "_P.bmp")

    shutil.copyfile(source_R, dest_R)
    shutil.copyfile(source_A, dest_A)
    shutil.copyfile(source_P, dest_P)
