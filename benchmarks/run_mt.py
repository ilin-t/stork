import argparse
import logging
import os
import shutil
from multiprocessing import Process
from os.path import basename, normpath

from src.log_modules.flag_repositories import get_repository_list
from src.stork_main import Stork
from src.log_modules import util
from src.log_modules.parse_repos import collect_resources, unzip, delete_repo, start_processes, join_processes, \
    aggregate_repositories
from src.log_modules.log_results import createLogger, closeLog


def list_folder_paths(path):
    return [f.path for f in os.scandir(path) if f.is_dir()]


def list_folder_names(path):
    return [f.name for f in os.scandir(path) if f.is_dir()]


def list_files_paths(path):
    return [f.path for f in os.scandir(path) if f.is_file()]


def list_files_names(path):
    return [f.name for f in os.scandir(path) if f.is_file()]


def filter_python_files(files):
    return [file for file in files if file.lower().endswith('.py')]


def filter_folders(project_path):
    folder_paths = list_folder_paths(project_path)
    folders = []
    ignore = False
    to_ignore = ['bin/*', 'www', 'js', 'virtual', '*virtual*', 'dist-packages', 'site-packages',
                 '*env*', 'env', 'etc/*', 'include/*', 'lib/*', 'lib64/*', '.venv/*', '*/venv/*']
    for folder in folder_paths:
        for name in to_ignore:
            if name in basename(normpath(folder)).lower():
                ignore = True
                break
        if ignore:
            continue
        # if "env" in basename(normpath(folder)).lower() or "lib" in basename(normpath(folder)).lower():
        #     continue
        elif basename(normpath(folder)).startswith((".", "_")):
            continue
        else:
            folders.append(folder)

    return folders


def run_stork(python_files, pipeline_logger, dataset_logger, read_method_logger, files_logger, error_logger):
    stork = Stork(r"/hpi/fs00/share/fg/rabl/ilin.tolovski/projects/stork/src/db_conn/config_s3.ini")
    stork.setClient(stork.access_key, stork.secret_access_key)

    for py_file in python_files:
        pipeline_logger.info(f"Pipeline: {py_file}")
        tree = []
        stork.assignVisitor.setLogger(error_logger)
        # stork.assignVisitor.setLoggerConfig("test_logger.log", "test", logging.INFO)

        try:
            tree = util.getAst(pipeline=py_file)
        except SyntaxError as e:
            error_logger.error("Logged from syntax error in run")
            error_logger.error(e)
            pipeline_logger.error(f"Pipeline {py_file} failed with the following error: {e}. Check the error logs.")

        if not tree:
            pipeline_logger.info(f"Pipeline {py_file} generated an empty AST. Check error logs.")

        error_logger.error(f"Pipeline {py_file} generated the following errors:")
        try:
            stork.assignVisitor.setPipeline(pipeline=py_file)
            stork.assignVisitor.visit(tree)
        except (AttributeError, KeyError, TypeError) as e:
            pipeline_logger.error(e)
        try:
            stork.assignVisitor.filter_Assignments()
            stork.assignVisitor.replace_variables_in_assignments()
            stork.assignVisitor.getDatasetsFromInputs()
            stork.assignVisitor.getDatasetsFromReadMethods()
        except RecursionError as e:
            pipeline_logger.info(e)

        # Add inputs and datasets to the global assignments and datasets dictionary
        stork.assignments[py_file] = stork.assignVisitor.inputs
        stork.datasets[py_file] = stork.assignVisitor.datasets

        error_logger.error("________________________________________________")
        pipeline_logger.info("________________________________________________")
        pipeline_logger.info(f"Pipeline {py_file} reads the following data files: ")
        print(f"Pipeline {py_file} accesses {len(stork.assignVisitor.datasets)} datasets.")
        pipeline_logger.info(f"Pipeline {py_file} accesses {len(stork.assignVisitor.datasets)} datasets.")
        print(f"Pipeline {py_file} accesses {len(stork.assignVisitor.inputs)} inputs.")
        pipeline_logger.info(f"Pipeline {py_file} accesses {len(stork.assignVisitor.inputs)} inputs.")
        # for input in stork.assignVisitor.inputs:
        #     pipeline_logger.info(f"\t Input: {input}")
        #     # print(f"Input: {input}")
        # pipeline_logger.info("________________________________________________")
        pipeline_logger.info("Datasets: ")
        for dataset in stork.assignVisitor.datasets:
            pipeline_logger.info(f"\t {dataset}")
        pipeline_logger.info("________________________________________________")

        for key in stork.assignVisitor.datasets_read_methods.keys():
            pipeline_logger.info(f"Datasets in {py_file} read via {key}")
            for dset_read_method in stork.assignVisitor.datasets_read_methods[key]:
                pipeline_logger.info(f"\t {dset_read_method}")
            pipeline_logger.info("\t ________________________________________________")
        repo_name = stork.assignVisitor.parseRepoName(stork.assignVisitor.getRepositoryName())
        buckets = stork.connector.getBucketNames()
        bucket_name = "stork-storage"
        stork.connector.createFolder(folder_name=repo_name, bucket=bucket_name)
        print(f"Adapted repository and bucket name: {repo_name}")
        new_pipeline = f"{py_file}_rewritten.py"
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
            print(stork.datasets[py_file])
            if len(stork.datasets[py_file]) > 0:
                dataset_logger.info({py_file: stork.datasets[py_file]})
            for dataset in stork.datasets[py_file]:
                print(f"Dataset: {dataset['dataset']}")
                if util.checkFileExtension(dataset['dataset']):
                    abs_path_dataset = stork.assignVisitor.parsePath(dataset['dataset'])
                    print(f"Source data file:{abs_path_dataset}")
                    # stork.connector.uploadFile(path=abs_path_dataset, folder=repo_name, bucket=bucket_name)
                    stork.connector.uploadFile(path=abs_path_dataset, folder=repo_name, logger=files_logger,
                                               bucket=bucket_name)
                    # dataset_name = stork.assignVisitor.getDatasetName(abs_path_dataset)
                    #
                    # print(f"Url: {stork.connector.getObjectUrl(key=dataset_name,folder=repo_name, bucket=bucket_name)}")
                    # # stork.assignVisitor.datasets_urls.append({"dataset_name": dataset,
                    # #                                           "url": stork.connector.getObjectUrl(
                    # #                                               key=dataset_name, folder=repo_name,
                    # #                                               bucket=bucket_name)})
                    #
                    # stork.assignVisitor.datasets_urls.append({"variable": dataset['variable'], "dataset_name": dataset['dataset'],
                    #                                          "url": stork.connector.getObjectUrl(
                    #                                              key=dataset_name, folder=repo_name,
                    #                                              bucket=bucket_name), "lineno": dataset['lineno']})

            pipeline_logger.info(f"Pipeline data set urls {stork.assignVisitor.datasets_urls}")
            stork.datasets_urls[py_file] = stork.assignVisitor.datasets_urls
            stork.read_methods[py_file] = stork.assignVisitor.read_methods
            stork.datasets_read_methods[py_file] = stork.assignVisitor.datasets_read_methods
            read_method_logger.info({"ds_read_methods": stork.datasets_read_methods[py_file]})
        except (OSError, TypeError, KeyError) as e:
            pipeline_logger.error(e)

        # self.assignVisitor.getDatasetsFromInputs()
        # self.assignVisitor.uploadDatasets(bucket=bucket_name)
        # print(f"Datasets_urls {py_file}: {stork.datasets_urls[py_file]}")
        stork.assignVisitor.transformScript(script=py_file, new_script=new_pipeline)
        print(f"Datasets_urls complete: {stork.datasets_urls}")
        util.reportAssign(stork.pipeline, stork.assignVisitor.assignments, "full")
        stork.assignVisitor.clearAssignments()
        stork.assignVisitor.clearInputs()
        stork.assignVisitor.clearDatasets()
        stork.assignVisitor.clearDatasetUrls()
        stork.assignVisitor.clearDatasetReadMethods()
        stork.assignVisitor.clearReadMethods()
        # print(stork.assignments)
        # print(stork.datasets)


def traverse_folders(path, project_logger, error_logger, dataset_logger, read_method_logger, files_logger):
    folders = filter_folders(path)
    files = list_files_paths(path)
    py_files = filter_python_files(files)

    if py_files:
        project_logger.info(f"Folder: {path}, executing the following python files:")
        for py_file in py_files:
            project_logger.info(f"\t {py_file}")
        run_stork(python_files=py_files, pipeline_logger=project_logger, error_logger=error_logger,
                  dataset_logger=dataset_logger, read_method_logger=read_method_logger, files_logger=files_logger)
    if folders:
        for folder in folders:
            traverse_folders(path=folder, project_logger=project_logger, error_logger=error_logger,
                             dataset_logger=dataset_logger, read_method_logger=read_method_logger, files_logger=files_logger)

    return 0


def analyze_repository(repos_to_run, repos_count, error_log, dataset_logger, read_method_logger, num_threads,
                       thread_id):
    # repositories = ["/home/ilint/HPI/repos/pipelines/trial/arguseyes.zip"]

    repos_per_thread = repos_count // num_threads
    start_index = thread_id * repos_per_thread
    end_index = start_index + repos_per_thread

    if thread_id == num_threads - 1:
        end_index = repos_count

    for i in range(start_index, end_index):
        repository = repos_to_run[i].strip()
        parent_dir, repo_name = unzip(repo_path=repository)
        projects = filter_folders(f"{parent_dir}/{repo_name}")
        # projects = filter_folders(f"/home/ilint/HPI/repos/pipelines/trial/arguseyes/")
        for project in projects:
            project_name = os.path.split(project)[1]
            print("________________________________________________________________________________________")
            print(f"Processing {project_name}, repository {projects.index(project) + 1} out of {len(projects)}")
            files_logger = createLogger(filename=f"{args.outputs}/individual_logs/{project_name}.log", project_name=project_name,
                                  level=logging.INFO)

            logger = createLogger(filename=f"{args.outputs}/individual_logs/{project_name}_files.log", project_name=f"{project_name}_files",
                                  level=logging.INFO)

            traverse_folders(path=project, project_logger=logger, error_logger=error_log, dataset_logger=dataset_logger,
                             read_method_logger=read_method_logger, files_logger=files_logger)

            closeLog(logger)

        shutil.rmtree(repository)


def main(args):
    NUM_THREADS = int(args.threads)
    processes = []
    # repos_to_run = collect_resources(root_folder=args.repositories)
    repos_to_run = get_repository_list(args.repositories)
    repos_count = len(repos_to_run)

    os.makedirs(f"{args.outputs}/errors/", exist_ok=True)
    os.makedirs(f"{args.outputs}/dataset_logs/", exist_ok=True)
    os.makedirs(f"{args.outputs}/individual_logs/", exist_ok=True)
    os.makedirs(f"{args.outputs}/read_method_logs/", exist_ok=True)

    for i in range(NUM_THREADS):
        error_log = createLogger(filename=f"{args.outputs}/errors/errors-{i}.log", project_name=f"error_log-{i}",
                                 level=logging.ERROR)

        dataset_logger = createLogger(filename=f"{args.outputs}/dataset_logs/dataset_logger-{i}.log",
                                      project_name=f"dataset_logger-{i}",
                                      level=logging.INFO)
        read_method_logger = createLogger(filename=f"{args.outputs}/read_method_logs/read_method_logger-{i}.log",
                                          project_name=f"read_method_logger-{i}",
                                          level=logging.INFO)
        processes.append(Process(target=analyze_repository, kwargs={"repos_to_run": repos_to_run,
                                                                    "repos_count": repos_count,
                                                                    "error_log": error_log,
                                                                    "dataset_logger": dataset_logger,
                                                                    "read_method_logger": read_method_logger,
                                                                    "num_threads": NUM_THREADS,
                                                                    "thread_id": i}))

    start_processes(processes)
    join_processes(processes)

    aggregate_repositories(f"{args.outputs}/dataset_logs/")
    aggregate_repositories(f"{args.outputs}/read_method_logs/")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Run Stork',
        description='Run Stork on a set of repositories',
    )

    # parser.add_argument('-r', '--repositories', default="/home/ilint/HPI/repos/pipelines/trial/")
    # parser.add_argument('-o', '--outputs', default="/home/ilint/HPI/repos/pipelines/results-trial/")
    # parser.add_argument('-r', '--repositories', default="/home/ilint/HPI/repos/pipelines/stork-zip-2days/repositories-test/")
    parser.add_argument('-r', '--repositories',
                        default="/home/ilint/HPI/Stork/results/27-10-stork-100k/repositories-mini/")
    parser.add_argument('-o', '--outputs', default="/home/ilint/HPI/Stork/results/27-10-stork-100k/")
    parser.add_argument('-t', '--threads', default=12)
    args = parser.parse_args()

    main(args)
