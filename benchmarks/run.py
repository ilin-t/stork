import argparse
import logging
import os
from os.path import basename, normpath

from src.stork import Stork
from src.log_modules import util
from src.log_modules.parse_repos import collect_resources, unzip, delete_repo
from src.log_modules.log_results import createLogger


# from src.log_modules.log_results import createLogger


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
    for folder in folder_paths:
        if "env" in basename(normpath(folder)).lower() or "lib" in basename(normpath(folder)).lower():
            continue
        elif basename(normpath(folder)).startswith((".", "_")):
            continue
        else:
            folders.append(folder)

    return folders


def run_switcheroo(python_files, pipeline_logger, error_logger):
    stork = Stork(r"../examples/db_playgrounds/config.ini")
    for py_file in python_files:
        pipeline_logger.info(f"Pipeline: {py_file}")
        tree = []

        try:
            tree = util.getAst(pipeline=py_file)
        except SyntaxError as e:
            error_logger.error("Logged from syntax error in run")
            error_logger.error(e)
            pipeline_logger.error(f"Pipeline {py_file} failed with the following error: {e}. Check the error logs.")
        # finally:
        #     tree=[]
        #     logger.info(f"Pipeline {py_file} generated an empty AST. Check error logs.")

        if not tree:
            pipeline_logger.info(f"Pipeline {py_file} generated an empty AST. Check error logs.")

        stork.assignVisitor.setLogger(error_logger)
        error_logger.error(f"Pipeline {py_file} generated the following errors:")

        stork.assignVisitor.setPipeline(pipeline=py_file)
        stork.assignVisitor.visit(tree)
        stork.assignVisitor.filter_Assignments()
        stork.assignVisitor.getDatasetsFromInputs()
        error_logger.error("________________________________________________")
        pipeline_logger.info("________________________________________________")
        pipeline_logger.info(f"Pipeline {py_file} reads the following data files: ")
        print(f"Pipeline {py_file} accesses {len(stork.assignVisitor.datasets)} datasets.")
        for dataset in stork.assignVisitor.datasets:
            pipeline_logger.info(f"\t {dataset}")
        pipeline_logger.info("________________________________________________")


def traverse_folders(path, project_logger, error_logger):
    folders = filter_folders(path)
    files = list_files_paths(path)
    py_files = filter_python_files(files)

    if py_files:
        project_logger.info(f"Folder: {path}, executing the following python files:")
        for py_file in py_files:
            project_logger.info(f"\t {py_file}")
        run_switcheroo(py_files, project_logger, error_logger)
    if folders:
        for folder in folders:
            traverse_folders(folder, project_logger, error_logger)

    return 0


def main(args):
    repositories = collect_resources(root_folder=args.repositories)
    error_log = createLogger(filename=f"{args.outputs}/logs/errors.log", project_name="error_log", level=logging.ERROR)
    # projects = filter_folders("/home/ilint/HPI/repos/read_csv_repos_300/test-run-1")
    for repository in repositories:
        parent_dir, repo_name = unzip(repo_path=repository)
        projects = filter_folders(f"{parent_dir}/{repo_name}")
        # projects = filter_folders("/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/repositories-test")
        # projects = filter_folders("/home/ilint/HPI/repos/read_csv_repos_300/repositories")
        # projects = filter_folders("/media/ilint/My Passport/HPI/stork/repositories")

        for project in projects:
            project_name = os.path.split(project)[1]
            print("________________________________________________________________________________________")
            print(f"Processing {project_name}, repository {projects.index(project) + 1} out of {len(projects)}")
            logger = createLogger(filename=f"{args.outputs}/logs/{project_name}.log", project_name=project_name, level=logging.INFO)

            traverse_folders(project, logger, error_log)

            delete_repo(project)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Run Stork',
        description='Run Stork on a set of repositories',
    )

    # --repositories = /mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/repositories-test/
    # --outputs = /mnt/fs00/rabl/ilin.tolovski/results/DATE-REPO-NAME

    parser.add_argument('-r', '--repositories')
    parser.add_argument('-o', '--outputs')

    args = parser.parse_args()
    os.makedirs(f"{args.outputs}/logs", exist_ok=True)
    main(args)
