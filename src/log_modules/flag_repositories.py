import argparse
import logging
import os
import shutil
from multiprocessing import Process

from src.log_modules.util import filter_folders
from src.log_modules.log_results import createLogger, createLoggerPlain, closeLog
from src.log_modules.parse_repos import unzip, start_processes, join_processes, aggregate_repositories
from src.ast.repo_marker import RepositoryMarker


def get_repository_list(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    f.close()

    return lines


def flag_repositories(repos_to_flag, repos_to_flag_count,
                      data_read_pipelines_py, data_read_pipelines_lib,
                      data_processing_repos_lib, data_processing_repos_py,
                      error_log, individual_logs, num_threads, thread_id):
    repos_per_thread = repos_to_flag_count // num_threads
    start_index = thread_id * repos_per_thread
    end_index = start_index + repos_per_thread

    print(f"Repos per thread: {repos_per_thread}")

    if thread_id == num_threads - 1:
        end_index = repos_to_flag_count

    for i in range(start_index, end_index):
        print(f"Thread {thread_id} processed {repos_to_flag[i]}")
        repository = repos_to_flag[i].strip()
        repo_marker = RepositoryMarker(repository)
        parent_dir, repo_name = unzip(repo_path=repository)
        projects = filter_folders(f"{parent_dir}/{repo_name}")

        for project in projects:
            print(f"Project: {project}")
            project_name = os.path.split(project)[1]
            print("________________________________________________________________________________________")
            print(f"Processing {project_name}, repository {projects.index(project) + 1} out of {len(projects)}")
            logger = createLogger(filename=f"{individual_logs}/{project_name}.log", project_name=project_name,
                                  level=logging.INFO)

            repo_marker.traverse_folders(path=project, project_logger=logger,
                                         error_logger=error_log,
                                         data_read_pipelines_lib=data_read_pipelines_lib,
                                         data_read_pipelines_py=data_read_pipelines_py)

            closeLog(logger)

        if repo_marker.flagged_repository_library:
            data_processing_repos_lib.info(repository)

        if repo_marker.flagged_repository_python:
            data_processing_repos_py.info(repository)

        shutil.rmtree(f"{parent_dir}/{repo_name}")


def main(args):
    NUM_THREADS = int(args.threads)

    os.makedirs(f"{args.outputs}", exist_ok=True)
    os.makedirs(f"{args.outputs}/repositories/library_reads/", exist_ok=True)
    os.makedirs(f"{args.outputs}/repositories/python_reads/", exist_ok=True)
    os.makedirs(f"{args.outputs}/pipelines/library_reads/", exist_ok=True)
    os.makedirs(f"{args.outputs}/pipelines/python_reads/", exist_ok=True)
    os.makedirs(f"{args.outputs}/individual_logs/", exist_ok=True)
    os.makedirs(f"{args.outputs}/errors/", exist_ok=True)

    repos_to_flag = get_repository_list("../../analysis_results/repository_list/local_list_repositories.txt")
    # repos_to_flag = get_repository_list(args.list_of_repos)
    # repos_to_flag = collect_resources_year(root_folder=args.repositories)
    repos_to_flag_count = len(repos_to_flag)
    processes = []

    for i in range(0, int(NUM_THREADS)):
        error_log = createLogger(filename=f"{args.outputs}/errors/errors-{i}.log", project_name=f"error_log-{i}",
                                 level=logging.ERROR)
        data_read_pipelines_lib = createLoggerPlain(
            filename=f"{args.outputs}/pipelines/library_reads/data_read_pipelines_lib-{i}.log",
            project_name=f"data_read_pipelines_lib-{i}",
            level=logging.INFO)
        data_read_pipelines_py = createLoggerPlain(
            filename=f"{args.outputs}/pipelines/python_reads/data_read_pipelines_py-{i}.log",
            project_name=f"data_read_pipelines_py-{i}", level=logging.INFO)

        data_processing_repos_lib = createLoggerPlain(
            filename=f"{args.outputs}/repositories/library_reads/data_processing_repos_lib-{i}.log",
            project_name=f"data_processing_repos_lib-{i}",
            level=logging.INFO)
        data_processing_repos_py = createLoggerPlain(
            filename=f"{args.outputs}/repositories/python_reads/data_processing_repos_py-{i}.log",
            project_name=f"data_processing_repos_py-{i}",
            level=logging.INFO)

        processes.append(Process(target=flag_repositories, kwargs={"repos_to_flag": repos_to_flag,
                                                                   "repos_to_flag_count": repos_to_flag_count,
                                                                   "data_read_pipelines_py": data_read_pipelines_py,
                                                                   "data_read_pipelines_lib": data_read_pipelines_lib,
                                                                   "data_processing_repos_lib": data_processing_repos_lib,
                                                                   "data_processing_repos_py": data_processing_repos_py,
                                                                   "error_log": error_log,
                                                                   "individual_logs": args.individual_logs,
                                                                   "num_threads": NUM_THREADS,
                                                                   "thread_id": i}))

    start_processes(processes)
    join_processes(processes)

    aggregate_repositories(f"{args.outputs}/pipelines/library_reads/")
    aggregate_repositories(f"{args.outputs}/pipelines/python_reads/")
    aggregate_repositories(f"{args.outputs}/repositories/library_reads/")
    aggregate_repositories(f"{args.outputs}/repositories/python_reads/")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Flag repositories and pipelines',
        description='Mark the data reading per repository and individual pipelines',
    )

    parser.add_argument('-t', '--threads', default=1)
    # parser.add_argument('-lr', '--list_of_repos',
    #                     default='/home/ilint/HPI/repos/stork/analysis_results/repository_list/local_list_repositories_old.txt')
    parser.add_argument('-r', '--repositories',
                        default='/home/ilint/HPI/repos/stork/analysis_results/repository_list/local_list_repositories_old.txt')
    parser.add_argument('-l', '--individual_logs',
                        default='/home/ilint/HPI/repos/stork/analysis_results/outputs_local_list_flag/individual_logs')
    parser.add_argument('-o', '--outputs', default='/home/ilint/HPI/repos/stork/analysis_results/outputs_local_list_flag')

    args = parser.parse_args()
    main(args)
    # print(collect_resources_year("/mnt/fs00/rabl/ilin.tolovski/repositories/stork-zip-full/repositories/year-2018/"))