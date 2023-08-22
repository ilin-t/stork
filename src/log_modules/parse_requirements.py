import argparse
import logging
import os
from multiprocessing import Process
from collections import Counter

import pandas as pd

from parse_repos import collect_resources, start_processes, join_processes, aggregate_repositories
from log_results import createLoggerPlain


def get_packages(filepath):
    DATA_PROCESSING_LIBRARIES = ['numpy', 'pandas', 'cudf', 'pyspark', 'spark', 'dask', 'arrow', 'duckdb', 'modin',
                                 'polars', 'dplyr',
                                 'clickhouse_connect', 'datatable']
    ML_LIBRARIES = ['scikit_learn', "torch", "torchvision", "torchaudio", "tensorflow", "tensorboard", "keras",
                    'theano']
    flag = False
    packages_per_file = []
    with open(f"{filepath}", "r") as file:
        for line in file.readlines():
            package = line.split("==")[0]
            package = package.split("<")[0]
            package = package.split(">")[0]
            package = package.strip()
            if package in DATA_PROCESSING_LIBRARIES or ML_LIBRARIES:
                flag = True
            packages_per_file.append(package)
    file.close()
    return flag, packages_per_file


def parse_requirement(requirements_files, package_count, results_path, repositories_path, flagged_repositories,
                      num_threads, thread_id):
    packages_per_thread = package_count // num_threads
    start_index = thread_id * packages_per_thread
    end_index = start_index + packages_per_thread
    total_packages = {}
    packages_list = []

    if thread_id == num_threads - 1:
        end_index = package_count - 1

    for i in range(start_index, end_index):
        flagged, packages_from_file = get_packages(requirements_files[i])
        requirements_file = get_filename(requirements_files[i])
        if flagged:
            flagged_repositories.info(msg=f"{repositories_path}{requirements_file}")
        total_packages[requirements_file] = packages_from_file

        packages_list.extend(packages_from_file)

    occurrences = Counter(packages_list)
    print(total_packages)
    with open(f"{results_path}/occurrences/occurrences-thread-{thread_id}.csv", "w") as file:
        file.write("library,count\n")
        for library, count in occurrences.items():
            if library == "":
                continue
            file.write(f'{str(library)},{str(count)}\n')
    file.close()


def aggregate_counts(results_root):
    occurrences_files = [x for x in os.scandir(f"{results_root}/occurrences/") if x.is_file()]
    total_occurrences = pd.DataFrame(columns=["library", "count"])
    for occurrences_file in occurrences_files:
        df = pd.read_csv(filepath_or_buffer=occurrences_file, header=0)
        total_occurrences = pd.concat([total_occurrences, df]).groupby(['library']).sum().reset_index()

    total_occurrences.sort_values(by="count", ascending=False, inplace=True)

    total_occurrences.to_csv(path_or_buf=f"{results_root}/occurrences/library_count_all_threads.csv")


def get_parent_dir(filepath):
    return os.path.dirname(filepath)


def get_filename(filepath):
    return os.path.basename(filepath)


def main(args):
    NUM_THREADS = int(args.threads)

    requirements_files = collect_resources(root_folder=args.packages)
    requirements_count = len(requirements_files)
    processes = []
    os.makedirs(f"{args.outputs}/occurrences/", exist_ok=True)
    os.makedirs(f"{args.outputs}/flagged/", exist_ok=True)
    for i in range(0, int(NUM_THREADS)):
        flagged_repositories = createLoggerPlain(filename=f"{args.outputs}/flagged/flagged_repositories-{i}.log",
                                                 project_name=f"flagged_repositories-{i}", level=logging.INFO)

        processes.append(Process(target=parse_requirement, kwargs={"requirements_files": requirements_files,
                                                                   "package_count": requirements_count,
                                                                   "results_path": args.outputs,
                                                                   "repositories_path": args.repositories,
                                                                   "flagged_repositories": flagged_repositories,
                                                                   "num_threads": NUM_THREADS,
                                                                   "thread_id": i}))

    start_processes(processes)
    join_processes(processes)
    aggregate_counts(args.outputs)
    aggregate_repositories(f"{args.outputs}/missing/")
    aggregate_repositories(f"{args.outputs}/flagged/")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Parse requirement files',
        description='Extract packages from all downloaded repositories',
    )

    parser.add_argument('-t', '--threads', default=12)
    parser.add_argument('-p', '--packages')
    parser.add_argument('-o', '--outputs')
    parser.add_argument('-r', '--repositories')

    args = parser.parse_args()
    main(args)
