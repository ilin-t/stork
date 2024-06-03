import argparse
import time

import pandas as pd
from openai import OpenAI
# from benchmarks.dolly_llm.run_dolly import read_file
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ORGANIZATION_ID = os.getenv('ORGANIZATION_ID')

def read_file(file):
    with open(file, "r") as f:
        content = f.read()
    f.close()
    # print(content)
    return content

def write_output(prompt_output, output_file):
    with open(output_file, "a+") as out:
        out.write(prompt_output)
    out.close()

def set_client(api_key, organization_id):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=api_key,
        organization=organization_id
    )
    return client

def process_pipeline(prompt_file, pipeline_file):
    start_prompt = time.time_ns()
    prompt_content = read_file(prompt_file)
    code_content = read_file(pipeline_file)
    read_time = (time.time_ns() - start_prompt) / 1000000

    pipeline_name = os.path.basename(pipeline_file).split(".")[0]

    return pipeline_name, prompt_content, code_content, read_time

def run_prompt(client, prompt, code, output_file):
    request_start = time.time_ns()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt + code
            }
        ],
        model="gpt-3.5-turbo",
    )
    request_end = (time.time_ns() - request_start) / 1000000

    print(f"Full response: {chat_completion}")
    print(f"Message response: {chat_completion.choices[0].message.content}")

    write_output(output_file=output_file, prompt_output=chat_completion.choices[0].message.content)

    return request_end

def prompt_wrapper(prompt_file, pipeline_file):
    pipeline_name, prompt_content, code_content, read_time = process_pipeline(prompt_file=prompt_file, pipeline_file=pipeline_file)

    client = set_client(api_key=OPENAI_API_KEY, organization_id=ORGANIZATION_ID)
    runtime = run_prompt(client, prompt=prompt_content, code=code_content, output_file=f"{args.output_path}gpt_output_{pipeline_name}.txt")

    return {"pipeline": pipeline_name, "prompt_time": read_time, "pipeline_time": runtime,
            "inference_time": runtime}


def main(args):
    results_rows = []
    py_files = [f.path for f in os.scandir(args.code_files_path) if f.is_file()]
    os.makedirs(args.output_path, exist_ok=True)
    for py_file in py_files:
        print(f"Currently processing: {py_file}.")
        results_rows.append(prompt_wrapper(prompt_file=args.prompt, pipeline_file=py_file))

    results = pd.DataFrame(results_rows)
    results.to_csv(f"{args.output_path}/{args.read_type}_results.tsv", sep="\t", mode='a', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Analyze a pipeline with GPT 3.5.',
        description='Run a prompt for a code file with GPT-3.5. The prompt and code are provided as input arguments.'
    )
    parser.add_argument('-p', '--prompt')
    parser.add_argument('-c', '--code_files_path')
    parser.add_argument('-o', '--output_path')
    parser.add_argument('-r', '--read_type')
    args = parser.parse_args()
    main(args)

