import argparse
import os
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
    prompt_time = (time.time_ns() - start_prompt)/1000000

    start_pipeline = time.time_ns()
    generate_text = pipeline(model="databricks/dolly-v2-12b", torch_dtype=torch.bfloat16, trust_remote_code=True,
                             device_map="auto", model_kwargs={'load_in_8bit': True})

    pipeline_time = (time.time_ns() - start_pipeline)/1000000

    start_inference = time.time_ns()
    res = generate_text(f"{prompt_content} \n {code_content}", do_sample=False)

    inference_time = (time.time_ns() - start_inference)/1000000

    pipeline_name = os.path.basename(pipeline_file).split(".")[0]

    with open(f"{args.output_path}dolly_output_{pipeline_name}.txt", "a+") as out:
        out.write(res[0]["generated_text"])
    out.close()

    return {"pipeline": pipeline_name, "prompt_time": prompt_time, "pipeline_time": pipeline_time, "inference_time": inference_time}


def main(args):

    results_rows=[]
    py_files = [f.path for f in os.scandir(args.code_files_path) if f.is_file()]
    os.makedirs(args.output_path, exist_ok=True)
    for py_file in py_files:
        print(f"Currently processing: {py_file}.")
        results_rows.append(process_pipeline(prompt_file=args.prompt, pipeline_file=py_file))

    results=pd.DataFrame(results_rows)
    results.to_csv(f"{args.output_path}/{args.read_type}_results.tsv", sep="\t", mode='a', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Analyze a pipeline with Dolly.',
        description='Run a prompt for a code file with Dolly. The prompt and code are provided as input arguments.'
    )
    parser.add_argument('-p', '--prompt')
    parser.add_argument('-c', '--code_files_path')
    parser.add_argument('-o', '--output_path')
    parser.add_argument('-r', '--read_type')
    args = parser.parse_args()
    main(args)
