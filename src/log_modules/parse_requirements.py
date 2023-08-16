import argparse
import logging
import os
from multiprocessing import Process
from collections import Counter

import pandas as pd

from parse_repos import collect_resources, start_processes, join_processes
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
    # print(f"{requirements_file}: {packages_per_file}")
    file.close()
    return flag, packages_per_file


def parse_requirement(requirements_files, package_count, packages_path, repositories_path, num_threads, thread_id):

    packages_per_thread = package_count // num_threads
    start_index = thread_id * packages_per_thread
    end_index = start_index + packages_per_thread
    # parsed_package_files = []
    total_packages = {}
    packages_list = []
    flagged_repositories = []

    if thread_id == num_threads - 1:
        end_index = package_count - 1

    for i in range(start_index, end_index):
        flagged, packages_from_file = get_packages(requirements_files[i])
        requirements_file = get_filename(requirements_files[i])
        if flagged:
            flagged_repositories.append(f"{repositories_path}{requirements_file}")
        # parsed_package_files.append(packages_list[i])
        total_packages[requirements_file] = packages_from_file

        packages_list.extend(packages_from_file)



    occurrences = Counter(packages_list)
    print(total_packages)
    with open(f"{packages_path}occurrences-thread-{thread_id}.csv", "w") as file:
        file.write("library,count\n")
        for library, count in occurrences.items():
            if library == "":
                continue
            file.write(f'{str(library)},{str(count)}\n')
    file.close()

    with open(f"{repositories_path}flagged_repositories-{thread_id}.txt", "w") as file:
        file.writelines(flagged_repositories)
    file.close()


def aggregate_counts(packages_root):
    occurrences_files = [x for x in os.scandir(packages_root) if x.is_file()]
    total_occurrences = pd.DataFrame(columns=["library", "count"])
    for occurrences_file in occurrences_files:
        df = pd.read_csv(filepath_or_buffer=occurrences_file, header=0)
        total_occurrences = pd.concat([total_occurrences, df]).groupby(['library']).sum().reset_index()

    total_occurrences.sort_values(by="count", ascending=False, inplace=True)

    total_occurrences.to_csv(path_or_buf=f"{packages_root}/library_count_all_threads.csv")


def get_parent_dir(filepath):
    return os.path.dirname(filepath)


def get_filename(filepath):
    return os.path.basename(filepath)


def main(args):
    NUM_THREADS = int(args.threads)

    requirements_files = collect_resources(root_folder=args.packages)
    requirements_count = len(requirements_files)
    processes = []

    for i in range(0, int(NUM_THREADS)):
        # missing_repositories = createLoggerPlain(filename=f"{OUTPUTS_ROOT}missing_repositories-{i}.log",
        #                                          project_name=f"missing_repositories-{i}", level=logging.INFO)
        # repositories_totals = createLoggerPlain(filename=f"{OUTPUTS_ROOT}/packages_stats-{i}.log",
        #                                         project_name=f"stats-{i}", level=logging.INFO)

        processes.append(Process(target=parse_requirement, kwargs={"requirements_files": requirements_files,
                                                                   "package_count": requirements_count,
                                                                   "packages_path": args.packages,
                                                                   "num_threads": NUM_THREADS,
                                                                   "thread_id": i}))

    start_processes(processes)
    join_processes(processes)
    aggregate_counts(args.packages)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Parse repositories',
        description='Extract packages from all downloaded repositories',
    )
    # REPOS_PATH = "/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/repositories-test/"
    # PACKAGES_PATH = "/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/packages/"
    # OUTPUTS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/outputs/"

    parser.add_argument('-t', '--threads', default=12)
    # parser.add_argument('-r', '--repos')
    parser.add_argument('-p', '--packages')
    parser.add_argument('-r', '--repositories')
    # parser.add_argument('-o', '--outputs')

    args = parser.parse_args()
    main(args)
