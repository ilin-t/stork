import argparse
import ast
import os

from src.log_modules.parse_repos import collect_resources_year
from src.log_modules.util import getAst


def direct_visit(parent_object, node, towards):
    func_name = "visit_" + type(towards).__name__
    func = getattr(parent_object, func_name)
    print(f"Method {func_name} will be called from node "
          f"type {type(node)} from object {type(parent_object)} towards object {type(towards)}.\n")
    output = func(towards)
    return output


def filter_pipeline(input_pipeline):
    tree = getAst(pipeline=input_pipeline)

    print(tree.body)
    flag = False
    for node in tree.body:
        if isinstance(node, ast.If):
            print("If condition")
            print(node.test)
            test = node.test
            try:
                print(f"Comparator value: {test.comparators[0].value}.")
                if test.comparators[0].value == 'main' or test.comparators[0].value == '__main__':
                    print("Detected main method, pipeline executable.")
                    # logger.info("Detected main method, pipeline executable.")
                    flag = True
            except AttributeError as e:
                print(e)

        elif isinstance(node, ast.Expr):
            flag=True

        elif isinstance(node, ast.FunctionDef):
            if node.name == 'main':
                print("Defined main method")

        elif isinstance(node, ast.Call):
            flag = True

    print(f"Pipeline {input_pipeline} processed. Executable status: {flag}.")
    return flag

def main(args):
    root_folder = "../examples/sample_pipelines/executable-pipelines/"
    # pipelines = [f.path for f in os.scandir(f"{root_folder}") if f.is_file()]
    pipelines = [f"{root_folder}setup.py"]
    count = 0
    executables = []
    non_executables = []

    NUM_THREADS = int(args.threads)

    os.makedirs(f"{args.outputs}/repositories/library_reads/", exist_ok=True)
    os.makedirs(f"{args.outputs}/repositories/python_reads/", exist_ok=True)
    os.makedirs(f"{args.outputs}/pipelines/library_reads/", exist_ok=True)
    os.makedirs(f"{args.outputs}/pipelines/python_reads/", exist_ok=True)
    os.makedirs(f"{args.outputs}/individual_logs/", exist_ok=True)
    os.makedirs(f"{args.outputs}/errors/", exist_ok=True)

    repos_to_flag = collect_resources_year(root_folder=args.repositories)
    repos_to_flag_count = len(repos_to_flag)
    processes = []

    for pipeline in pipelines:
        executable = filter_pipeline(input_pipeline=pipeline)
        if executable:
            executables.append(pipeline)
        else:
            non_executables.append((pipeline))
    print(f"Number of executable pipelines: {len(executables)}")
    print(executables)
    print(f"Number of non-executable pipelines: {len(non_executables)}")
    print(non_executables)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='Filter the executable pipelines from the general collection of repositories.',
        description='Based on the structure of the pipeline, '
                    'collect the name and paths to the executable pipelines in all the repositories.',
    )

    parser.add_argument('-t', '--threads', default=1)
    parser.add_argument('-r', '--repositories',
                        default='/home/ilint/HPI/repos/stork/analysis_results/repository_list/local_list_repositories_old.txt')
    parser.add_argument('-l', '--individual_logs',
                        default='/home/ilint/HPI/repos/stork/analysis_results/outputs_local_list/individual_logs')
    parser.add_argument('-o', '--outputs', default='/home/ilint/HPI/repos/stork/analysis_results/outputs_local_list_flag')

    args = parser.parse_args()
    main(args)
