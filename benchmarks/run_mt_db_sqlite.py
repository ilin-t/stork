import argparse
import logging
import os
import shutil
import sys
import time
from multiprocessing import Process

import numpy as np
import pandas as pd

from src.ast.assign_visitor import getDatasetName
from src.log_modules.util import filter_folders, list_files_paths, filter_python_files
from src.log_modules.flag_repositories import get_repository_list
from src.stork_db import Stork
from src.log_modules import util
from src.log_modules.parse_repos import unzip, start_processes, join_processes, \
    aggregate_repositories
from src.log_modules.log_results import createLogger, closeLog, createLoggerPlain


def run_stork(python_files, flagged_pipelines, pipeline_logger, dataset_logger, existent_dataset_logger,read_method_logger,
              translated_datasets_logger, error_logger, yearly_stats_thread, pipelines_to_rewrite_logger):

    yearly_stats_thread["pipelines_total"] = yearly_stats_thread["pipelines_total"] + len(python_files)
    stork = Stork(logger= pipeline_logger, config_path=f"db_sqlite.db", connector="sqlite")
    # print(f"Flagged files: {flagged_pipelines}")
    for py_file in python_files:
        if py_file in flagged_pipelines:

            pipeline_logger.info(f"Pipeline: {py_file}")
            tree = []
            stork.assignVisitor.setLogger(error_logger)

            try:
                tree = util.getAst(pipeline=py_file)
            except SyntaxError as e:
                error_logger.error(e)
                pipeline_logger.error(f"Pipeline {py_file} failed with the following error: {e}. Check the error logs.")

            if not tree:
                pipeline_logger.info(f"Pipeline {py_file} generated an empty AST. Check error logs.")

            error_logger.error(f"Pipeline {py_file} generated the following errors:")
            try:
                stork.setPipeline(pipeline=py_file)
                stork.assignVisitor.setPipeline(pipeline=py_file)
                stork.assignVisitor.visit(tree)

            except (AttributeError, KeyError, TypeError) as e:
                pipeline_logger.error(e)
            try:
                stork.assignVisitor.filter_Assignments()
                stork.assignVisitor.replace_variables_in_assignments()
                # stork.assignVisitor.setVariables()
                stork.assignVisitor.getDatasetsFromInputs()
                stork.assignVisitor.getDatasetsFromReadMethods()
            except RecursionError as e:
                pipeline_logger.info(e)
                continue

            # repo_name = stork.assignVisitor.parseRepoName(stork.assignVisitor.getRepositoryName())
            repo_name = py_file.split("/page-")[1]
            repo_name = repo_name.split("/")
            repo_name = repo_name[1]
            stork.assignments[py_file] = stork.assignVisitor.inputs
            stork.datasets[py_file] = stork.assignVisitor.datasets

            yearly_stats_thread["pipelines_processed"] = yearly_stats_thread["pipelines_processed"] + 1

            error_logger.error("________________________________________________")
            pipeline_logger.info("________________________________________________")
            pipeline_logger.info(f"Pipeline {py_file} reads the following data files: ")
            # print(f"Pipeline {py_file} accesses {len(stork.assignVisitor.datasets)} datasets.")
            pipeline_logger.info(f"Pipeline {py_file} accesses {len(stork.assignVisitor.datasets)} datasets.")
            # print(f"Pipeline {py_file} accesses {len(stork.assignVisitor.inputs)} inputs.")
            pipeline_logger.info(f"Pipeline {py_file} accesses {len(stork.assignVisitor.inputs)} inputs.")
            # for input in stork.assignVisitor.inputs:
            #     pipeline_logger.info(f"\t Input: {input}")
            #     # print(f"Input: {input}")
            pipeline_logger.info("________________________________________________")
            schema_name = ''.join([i for i in repo_name if i.isalpha()])
            if len(stork.datasets[py_file]) > 0:
                # stork.connector.create_schema(schema_name, "postgres-default-admin")
                print(f"Adapted repository and bucket name: {repo_name}")
                # Add inputs and datasets to the global assignments and datasets dictionary
                yearly_stats_thread["total_datasets"] = (yearly_stats_thread["total_datasets"]
                                                         + len(stork.datasets[py_file]))

                yearly_stats_thread["pipelines_success"] = (yearly_stats_thread["pipelines_success"] + 1)
            else:
                yearly_stats_thread["pipelines_failed"] = (yearly_stats_thread["pipelines_failed"] + 1)

            pipeline_logger.info("Datasets: ")
            for dataset in stork.assignVisitor.datasets:
                pipeline_logger.info(f"\t {dataset}")
            pipeline_logger.info("________________________________________________")

            for key in stork.assignVisitor.datasets_read_methods.keys():
                yearly_stats_thread[f"read_{key}"] = (yearly_stats_thread[f"read_{key}"] +
                                                      len(stork.assignVisitor.datasets_read_methods[key]))
                yearly_stats_thread[f"total_reads_classified"] = (yearly_stats_thread[f"total_reads_classified"] +
                                                                  len(stork.assignVisitor.datasets_read_methods[key]))
                pipeline_logger.info(f"Datasets in {py_file} read via {key}")
                for dset_read_method in stork.assignVisitor.datasets_read_methods[key]:
                    pipeline_logger.info(f"\t {dset_read_method}")
                pipeline_logger.info("\t ________________________________________________")
            pipeline_name = py_file.split("/")
            pipeline_name = pipeline_name[-1]
            new_pipeline = f"{args.outputs}/rewritten_pipelines/{pipeline_name[:-3]}_rewritten.py"
            # if repo_name not in buckets:
            #     self.connector.createBucket(bucket_name=bucket_name, region="eu-central-1")
            #     print(f"Should create bucket: {bucket_name}")

            # try:
            # for member in stork.assignVisitor.inputs:
            #     for source in member["data_source"]:
            #         for dataset in source["data_file"]:
            #             if util.checkFileExtension(dataset):
            # print(f"dataset:{dataset}")
            try:
                # print(stork.datasets[py_file])
                for dataset in stork.datasets[py_file]:
                    print(f"Dataset: {dataset['dataset']}")
                    abs_path_dataset = stork.assignVisitor.parsePath(dataset)
                    print(f"Abs Dataset: {abs_path_dataset}")
                    dataset_logger.info(abs_path_dataset)
                    if abs_path_dataset and util.fileExists(abs_path_dataset):
                        existent_dataset_logger.info(abs_path_dataset)
                        print(f"Source data file:{abs_path_dataset}")
                        dataset_df = stork.connector.read_file(abs_path_dataset)
                        dataset_name = getDatasetName(abs_path_dataset)
                        dataset_name = ''.join([i for i in dataset_name if i.isalpha()])
                        # stork.connector.uploadFile(path=abs_path_dataset, folder=repo_name, bucket=bucket_name)
                        df_size = sys.getsizeof(dataset_df)
                        pipeline_logger.info(f"Dataset size: {df_size}")

                        schema_string = stork.connector.generate_schema(dataset_df)

                        if stork.connector.create_table(table_name=f"{schema_name}_{dataset_name}",
                                                       schema_order=schema_string):
                            insert_start = time.time_ns()
                            # if stork.connector.insert_into_table(table_name=f"{schema_name}.{dataset_name}",
                            #                                     schema=schema_string, data=dataset_df):
                            stork.connector.get_schema(f"{dataset_name}")
                            translated_datasets_logger.info(abs_path_dataset)

                        else:
                            pipeline_logger.info(f"Failed to create table for {dataset_name} from {py_file}.")

                        yearly_stats_thread["dataset_exists"] = yearly_stats_thread["dataset_exists"] + 1
                        yearly_stats_thread["pipeline_rewritten"] = yearly_stats_thread["pipeline_rewritten"] + 1


                        stork.assignVisitor.datasets_urls.append(
                            {"variable": dataset['variable'], "dataset_name": dataset['dataset'],
                             "url": f"{schema_name}.{dataset_name}", "lineno": dataset['lineno']})
                        stork.datasets_urls[py_file] = stork.assignVisitor.datasets_urls

                        pipelines_to_rewrite_logger.info(
                            {"pipeline": py_file, "dataset_urls": stork.datasets_urls[py_file]})

                        stork.assignVisitor.transformScript(script=py_file, new_script=new_pipeline,
                                                            datasets_urls=stork.assignVisitor.datasets_urls)
                #
                # print(f"Url: {stork.connector.getObjectUrl(key=dataset_name,folder=repo_name, bucket=bucket_name)}")
                # # stork.assignVisitor.datasets_urls.append({"dataset_name": dataset,
                # #                                           "url": stork.connector.getObjectUrl(
                # #                                               key=dataset_name, folder=repo_name,
                # #                                               bucket=bucket_name)})
                pipeline_logger.info(f"Pipeline data set urls {stork.assignVisitor.datasets_urls}")
                stork.datasets_urls[py_file] = stork.assignVisitor.datasets_urls
                print(stork.datasets_urls[py_file])
                stork.read_methods[py_file] = stork.assignVisitor.read_methods
                stork.datasets_read_methods[py_file] = stork.assignVisitor.datasets_read_methods
                read_method_logger.info({"ds_read_methods": stork.datasets_read_methods[py_file]})
            except (OSError, TypeError, KeyError) as e:
                pipeline_logger.error(e)

            # self.assignVisitor.getDatasetsFromInputs()
            # self.assignVisitor.uploadDatasets(bucket=bucket_name)
            # print(f"Datasets_urls {py_file}: {stork.datasets_urls[py_file]}")
            #
            # print(f"Datasets_urls complete: {stork.datasets_urls}")
            # util.reportAssign(stork.pipeline, stork.assignVisitor.assignments, "full")
            stork.assignVisitor.clearAssignments()
            stork.assignVisitor.clearInputs()
            stork.assignVisitor.clearDatasets()
            stork.assignVisitor.clearDatasetUrls()
            stork.assignVisitor.clearDatasetReadMethods()
            stork.assignVisitor.clearReadMethods()
            # print(stork.assignments)
            # print(stork.datasets)


def traverse_folders(path, yearly_stats_thread, flagged_pipelines, project_logger, error_logger, dataset_logger, read_method_logger,
                     files_logger, pipelines_to_rewrite_logger, existent_dataset_logger, translated_datasets_logger):
    folders = filter_folders(path)
    files = list_files_paths(path)
    py_files = filter_python_files(files)

    if py_files:
        project_logger.info(f"Folder: {path}, executing the following python files:")
        for py_file in py_files:
            project_logger.info(f"\t {py_file}")
        run_stork(python_files=py_files, flagged_pipelines = flagged_pipelines, pipeline_logger=project_logger, error_logger=error_logger,
                  dataset_logger=dataset_logger, read_method_logger=read_method_logger,
                  yearly_stats_thread=yearly_stats_thread,
                  pipelines_to_rewrite_logger=pipelines_to_rewrite_logger, existent_dataset_logger=existent_dataset_logger,
                  translated_datasets_logger=translated_datasets_logger)
    if folders:
        for folder in folders:
            traverse_folders(path=folder, flagged_pipelines=flagged_pipelines, project_logger=project_logger, error_logger=error_logger,
                             dataset_logger=dataset_logger, read_method_logger=read_method_logger,
                             files_logger=files_logger, yearly_stats_thread=yearly_stats_thread,
                             pipelines_to_rewrite_logger=pipelines_to_rewrite_logger, existent_dataset_logger=existent_dataset_logger,
                            translated_datasets_logger=translated_datasets_logger)

    return 0


def analyze_repository(repos_to_run, flagged_pipelines, yearly_stats_thread, repos_count, error_log, dataset_logger, read_method_logger,
                       num_threads, thread_id, existent_datasets_logger, translated_datasets_logger, pipelines_to_rewrite_logger):
    # repositories = ["/home/ilint/HPI/repos/pipelines/trial/arguseyes.zip"]

    repos_per_thread = repos_count // num_threads
    start_index = 0
    end_index = 0
    # if split == 2:
    #     start_index = repos_count + ((thread_id) * repos_per_thread)
    #     end_index = start_index + repos_per_thread
    #
    # elif split == 1:
    #     start_index = (thread_id * repos_per_thread)
    #     end_index = start_index + repos_per_thread

    print(f"Start index: {start_index}")
    print(f"End index: {end_index}")

    start_index = (thread_id * repos_per_thread)
    end_index = start_index + repos_per_thread
    yearly_stats_thread["thread_id"] = thread_id
    yearly_stats_thread["total_repositories"] = repos_count
    yearly_stats_thread["repositories_per_thread"] = repos_per_thread

    if thread_id == num_threads - 1:
        end_index = repos_count

    for i in range(start_index, end_index):
        failed_repos = []
        repository = repos_to_run[i].strip()
        parent_dir, repo_name = unzip(repo_path=repository)
        assert parent_dir, repo_name
        projects = filter_folders(f"{parent_dir}/{repo_name}")
        # projects = filter_folders(f"/home/ilint/HPI/repos/pipelines/trial/arguseyes/")
        for project in projects:
            try:
                project_name = os.path.split(project)[1]
                print("________________________________________________________________________________________")
                print(
                    f"Thread {thread_id} processes {project_name}, repository {i - start_index + 1} "
                    f"out of {end_index - start_index}")
                files_logger = createLogger(filename=f"{args.outputs}/individual_logs/{project_name}_files.log",
                                            project_name=f"{project_name}_files",
                                            level=logging.INFO)

                logger = createLogger(filename=f"{args.outputs}/individual_logs/{project_name}.log",
                                      project_name=f"{project_name}",
                                      level=logging.INFO)

                traverse_folders(path=project, flagged_pipelines = flagged_pipelines, project_logger=logger, error_logger=error_log,
                                 dataset_logger=dataset_logger, yearly_stats_thread=yearly_stats_thread,
                                 read_method_logger=read_method_logger, files_logger=files_logger,
                                 pipelines_to_rewrite_logger=pipelines_to_rewrite_logger, existent_dataset_logger=existent_datasets_logger,
                                 translated_datasets_logger=translated_datasets_logger)

                closeLog(logger)
                yearly_stats_thread["repositories_processed"] = yearly_stats_thread["repositories_processed"] + 1
            except (OSError, TypeError, SyntaxError, FileNotFoundError) as e:
                failed_repos.append(project)
                print(e)
                print(f"REPO NOT PROCESSED: {project}")

            yearly_stats_thread.to_csv(f"{args.outputs}/yearly-stats-{thread_id}.tsv", sep="\t")

        time.sleep(0.5)
        shutil.rmtree(path = repository, ignore_errors = True)


def aggregate_stats(dir_path):
    list_of_stats = [f for f in os.listdir(path=dir_path) if f"yearly-stats" in f]
    print(list_of_stats)
    agg_stats = pd.DataFrame(
        columns=["thread_id", "total_repositories", "repositories_per_thread", "repositories_processed",
                 "pipelines_total", "pipelines_processed", "pipelines_success",
                 "pipelines_failed", "success_rate", "total_datasets", "reads_per_pipeline",
                 "read_variable", "read_var_pct", "read_raw_string", "read_str_pct",
                 "read_external", "read_external_pct", "total_reads_classified", "dataset_exists",
                 "dataset_exists_pct", "pipeline_rewritten", "existent_datasets", "translated_datasets",
                 "repositories_successful", "repositories_success_rate"]
    )
    for stats in list_of_stats:
        df_year = pd.read_csv(f"{dir_path}/{stats}", sep='\t')
        agg_stats = pd.concat(objs=[df_year, agg_stats], axis=0, copy=True)

    cols_to_sum = ["repositories_processed", "pipelines_total", "pipelines_processed", "pipelines_success",
                   "pipelines_failed", "total_datasets", "read_variable", "read_raw_string", "read_external",
                   "total_reads_classified", "dataset_exists", "existent_datasets", "translated_datasets",
                   "pipeline_rewritten", "repositories_successful"]

    agg_stats.loc['Total'] = agg_stats[cols_to_sum].sum(axis=0)

    agg_stats['success_rate'] = agg_stats['pipelines_success'] / agg_stats['pipelines_processed']
    agg_stats['reads_per_pipeline'] = agg_stats['total_datasets'] / agg_stats['pipelines_success']

    agg_stats['read_var_pct'] = agg_stats['read_variable'] / agg_stats['total_datasets']
    agg_stats['read_str_pct'] = agg_stats['read_raw_string'] / agg_stats['total_datasets']
    agg_stats['read_external_pct'] = agg_stats['read_external'] / agg_stats['total_datasets']
    agg_stats['dataset_exists_pct'] = agg_stats['dataset_exists'] / agg_stats['total_datasets']

    agg_stats.to_csv(f"{dir_path}/aggregated-stats.tsv", sep="\t")


def main(args):
    NUM_THREADS = int(args.threads)
    processes = []
    # SPLIT_INTO = args.split
    # repos_to_run = collect_resources(root_folder=args.repositories)
    repos_to_run = get_repository_list(args.repositories)
    flagged_pipelines = get_repository_list(args.pipelines)
    flagged_pipelines = [pipeline.strip() for pipeline in flagged_pipelines]
    # repos_count = len(repos_to_run) // 2
    repos_count = len(repos_to_run)

    os.makedirs(f"{args.outputs}/errors/", exist_ok=True)
    os.makedirs(f"{args.outputs}/dataset_logs/", exist_ok=True)
    os.makedirs(f"{args.outputs}/existent_dataset_logs/", exist_ok=True)
    os.makedirs(f"{args.outputs}/translated_dataset_logs/", exist_ok=True)
    os.makedirs(f"{args.outputs}/individual_logs/", exist_ok=True)
    os.makedirs(f"{args.outputs}/read_method_logs/", exist_ok=True)
    os.makedirs(f"{args.outputs}/rewritten_pipelines/", exist_ok=True)
    os.makedirs(f"{args.outputs}/rewrite_logs/", exist_ok=True)

    yearly_stats_threads = []

    for i in range(NUM_THREADS):
        error_log = createLogger(filename=f"{args.outputs}/errors/errors-{i}.log", project_name=f"error_log-{i}",
                                 level=logging.ERROR)

        dataset_logger = createLogger(filename=f"{args.outputs}/dataset_logs/dataset_logger-{i}.log",
                                      project_name=f"dataset_logger-{i}",
                                      level=logging.INFO)

        existent_datasets_logger = createLoggerPlain(filename=f"{args.outputs}/existent_dataset_logs/existent_dataset_logger-{i}.log",
                                      project_name=f"existent_dataset_logger-{i}",
                                      level=logging.INFO)

        translated_datasets_logger = createLoggerPlain(filename=f"{args.outputs}/translated_dataset_logs/translated_dataset_logger-{i}.log",
                                      project_name=f"translated_dataset_logger-{i}",
                                      level=logging.INFO)

        pipelines_to_rewrite_logger = createLogger(filename=f"{args.outputs}/rewrite_logs/pipelines_to_rewrite-{i}.log",
                                                   project_name=f"pipelines_to_rewrite-{i}",
                                                   level=logging.INFO)

        read_method_logger = createLogger(filename=f"{args.outputs}/read_method_logs/read_method_logger-{i}.log",
                                          project_name=f"read_method_logger-{i}",
                                          level=logging.INFO)

        yearly_stats_threads.append(pd.DataFrame(
            columns=["thread_id", "total_repositories", "repositories_per_thread", "repositories_processed",
                 "pipelines_total", "pipelines_processed", "pipelines_success",
                 "pipelines_failed", "success_rate", "total_datasets", "reads_per_pipeline",
                 "read_variable", "read_var_pct", "read_raw_string", "read_str_pct",
                 "read_external", "read_external_pct", "total_reads_classified", "dataset_exists",
                 "dataset_exists_pct", "pipeline_rewritten", "existent_datasets",
                     "translated_datasets", "repositories_successful", "repositories_success_rate"],
            data=np.zeros(shape=(1, 25)), index=[i]))

        processes.append(Process(target=analyze_repository, kwargs={"repos_to_run": repos_to_run,
                                                                    "flagged_pipelines": flagged_pipelines,
                                                                    "yearly_stats_thread": yearly_stats_threads[i],
                                                                    "repos_count": repos_count,
                                                                    "error_log": error_log,
                                                                    "dataset_logger": dataset_logger,
                                                                    "read_method_logger": read_method_logger,
                                                                    "num_threads": NUM_THREADS,
                                                                    "thread_id": i,
                                                                    "existent_datasets_logger": existent_datasets_logger,
                                                                    "translated_datasets_logger":translated_datasets_logger,
                                                                    # "split": SPLIT_INTO,
                                                                    "pipelines_to_rewrite_logger": pipelines_to_rewrite_logger
                                                                    }))


    start_processes(processes)
    join_processes(processes)

    aggregate_repositories(f"{args.outputs}/dataset_logs/")
    aggregate_repositories(f"{args.outputs}/read_method_logs/")
    aggregate_repositories(f"{args.outputs}/rewrite_logs/")
    aggregate_repositories(f"{args.outputs}/existent_dataset_logs/")
    aggregate_repositories(f"{args.outputs}/translated_dataset_logs/")
    aggregate_stats(f"{args.outputs}")


if __name__ == '__main__':
    # aggregate_stats("test-2021/")
    parser = argparse.ArgumentParser(
        prog='Run Stork',
        description='Run Stork on a set of repositories',
    )

    # parser.add_argument('-r', '--repositories', default="/home/ilint/HPI/repos/pipelines/trial/")
    # parser.add_argument('-o', '--outputs', default="/home/ilint/HPI/repos/pipelines/results-trial/")
    # parser.add_argument('-s', '--split', default=2)
    # parser.add_argument('-s', '--split', default=1)
    parser.add_argument('-r', '--repositories',
                        default="/home/ilint/HPI/repos/stork/analysis_results/outputs_local_list_flag/repositories/library_reads/aggregated_results.txt")
    parser.add_argument('-p', '--pipelines',
                        default="/home/ilint/HPI/repos/stork/analysis_results/outputs_local_list_flag/pipelines/library_reads/aggregated_results.txt")
    parser.add_argument('-o', '--outputs', default="/home/ilint/HPI/repos/stork/analysis_results/outputs_local_list/")
    parser.add_argument('-t', '--threads', default=6)
    args = parser.parse_args()

    main(args)
