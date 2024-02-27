import argparse

import torch
import time
from transformers import pipeline
import pandas as pd


def read_file(file):
    with open(file, "rb") as f:
        content = f.read()
    f.close()
    print(content)
    return content


def process_pipeline(prompt_file, pipeline_file):
    start_prompt = time.time_ns()
    prompt_content = read_file(prompt_file)
    code_content = read_file(pipeline_file)
    prompt_time = time.time_ns() - start_prompt

    start_pipeline = time.time_ns()
    generate_text = pipeline(model="databricks/dolly-v2-12b", torch_dtype=torch.bfloat16, trust_remote_code=True,
                             device_map="auto")

    pipeline_time = time.time_ns() - start_pipeline

    start_inference = time.time_ns()
    res = generate_text(f"{prompt_content} \n {code_content}", do_sample=False)
    inference_time = time.time_ns() - start_inference

    pipeline_name = pipeline_file.split(".")[0]

    with open(f"dolly_output_{pipeline_name}.txt", "w") as out:
        out.write(res[0]["generated_text"])
    out.close()

    return {"pipeline": pipeline_name, "prompt_time": prompt_time, "pipeline_time": pipeline_time, "inference_time": inference_time}


def main(args):

    try:
        results=pd.read_csv(args.output_file, sep="\t")

    except FileNotFoundError:
        results = pd.DataFrame(columns=["pipeline", "prompt_time", "pipeline_time", "inference_time"])

    for py_file in args.code:
        results.loc[-1] = process_pipeline(prompt_file=args.prompt, pipeline_file=py_file)


    results.to_csv(args.output_file, sep="\t", mode='a', index=False)






if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Analyze a pipeline with Dolly.',
        description='Run a prompt for a code file with Dolly. The prompt and code are provided as input arguments.'
    )
    parser.add_argument('-p', '--prompt')
    parser.add_argument('-c', '--code')
    parser.add_argument('-o', '--output_file')
    args = parser.parse_args()
    main(args)

"""Find where data is being ingested in the following code, and return the path of the dataset.

import numpy as np
import pickle
from utils.data_util import *
from numpy.lib.npyio import save
from GAN_model import *


if __name__ == "__main__":
    
    print("Loading data...")
    # X_train = pickle.load(open("X_train_aa.pkl", "rb"))  # --> load AA dataset
    X_train = pickle.load(open("X_train_af.pkl", "rb"))  # --> load AF dataset
    y = pickle.load(open('y_af.pkl', 'rb'))
    dataloader = DataLoader()
    X_train = dataloader.pick_type_only(X_train, y, 1) # pick AF ECG only

    EPOCHS = 10000
    LATENT_SIZE = 100
    SAVE_INTRIVAL = 100
    SAVE_MODEL_INTERVAL = 1000
    BATCH_SIZE = 128
    # INPUT_SHAPE = (216, 1)  # --> AA dataset
    INPUT_SHAPE = (180, 1)  # --> AF dataset
    RANDOM_SINE = False
    SCALE = 2 
    MINIBATCH = True # use minibatch discrimination to avoid mode collapse
    SAVE_MODEL = True
    SAVE_REPORT = True
    GEN_VERSION = 0  # 0 use default generator, 1 ~ 5 use generator from in_progress
    dcgan = DCGAN(INPUT_SHAPE, LATENT_SIZE, random_sine=RANDOM_SINE, scale=SCALE, minibatch=MINIBATCH, gen_version=GEN_VERSION) 
    X_train = dcgan.specify_range(X_train, -2, 2)/2 # limit the signal range [-2, 2], scale by divid 2 
    X_train = X_train.reshape(-1, INPUT_SHAPE[0], INPUT_SHAPE[1])
    print('Training...')
    dcgan.train(EPOCHS, X_train, BATCH_SIZE, SAVE_INTRIVAL, save=SAVE_MODEL, save_model_interval=SAVE_MODEL_INTERVAL, 
                save_report=SAVE_REPORT)
    print("Complete!!!")

"""
