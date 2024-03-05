import argparse
import logging
import os
import shutil
import time

from glob import glob

from src.log_modules import util
from src.ast.assign_visitor import AssignVisitor, getDatasetName
from src.log_modules.log_results import createLogger, createLoggerPlain


class Stork:

    def __init__(self, logger):
        self.assignVisitor = AssignVisitor()
        self.pipeline = ""
        self.logger = logger
        self.config_path = None
        self.config = None
        self.assignments = {}
        self.datasets = {}
        self.datasets_urls = {}
        self.read_methods = {}
        self.datasets_read_methods = {}
        self.translation_times = {}
        self.schema_generation_times = {}
        self.table_creation_times = {}
        self.table_insertion_times = {}
        self.dataframe_sizes = {}

    def setPipeline(self, pipeline):
        self.pipeline = pipeline

    def rewritePipeline(self, pipeline):

        try:
            script_name, file_ending = pipeline.split(".")
            self.assignVisitor.transformScript(script=pipeline, new_script=script_name + "_new." + file_ending,
                                               datasets_urls=self.datasets_urls)
        except len(pipeline.split(".")) > 2:
            print("Pipeline name has wrong formatting.")

    def setup(self, pipeline, new_pipeline, destination_path):

        self.setPipeline(pipeline=pipeline)
        self.assignVisitor.setPipeline(pipeline=self.pipeline)
        self.assignVisitor.setLoggerConfig("test-logger.log", "test", logging.INFO)

        translation_start = time.time_ns()
        tree = util.getAst(pipeline=pipeline)
        self.assignVisitor.visit(tree)
        self.assignVisitor.filter_Assignments()
        self.assignVisitor.getDatasetsFromReadMethods()
        self.assignVisitor.replace_variables_in_assignments()
        self.assignVisitor.getDatasetsFromInputs()
        translation_end = time.time_ns() - translation_start

        self.translation_times = translation_end / 1000000
        self.logger.info(f"Translation time: {translation_end / 1000000} ms")

        print(self.assignVisitor.datasets)
        self.logger.info(f"Stork detected the following datasets: {self.assignVisitor.datasets}")
        for dataset in self.assignVisitor.datasets:
            abs_path_dataset = self.assignVisitor.parsePath(dataset)
            print(f"Absolute path: {abs_path_dataset}")
            if abs_path_dataset and util.fileExists(abs_path_dataset):
                dataset_name = getDatasetName(abs_path_dataset)
                dataset_name = ''.join([i for i in dataset_name if i.isalnum()])
                schema_gen_start = time.time_ns()
                schema_gen_end = time.time_ns() - schema_gen_start
                self.logger.info(f"Schema generation for {dataset_name}: {schema_gen_end / 1000000} ms")
                self.schema_generation_times[dataset_name] = (schema_gen_end / 1000000)
                print(dataset_name)

                insert_start = time.time_ns()
                shutil.copy(abs_path_dataset, f"{destination_path}/{dataset_name}.csv")
                insert_end = time.time_ns() - insert_start
                self.table_insertion_times[dataset_name] = (insert_end / 1000000)
                self.logger.info(f"Insertion time for {dataset_name}: {insert_end / 1000000}ms")
                self.assignVisitor.datasets_urls.append({"variable": dataset['variable'], "dataset_name": dataset['dataset'],
                                                         "url": f"{destination_path}{dataset_name}.csv", "lineno": dataset['lineno']})
                self.logger.info(self.assignVisitor.datasets_urls)
                self.assignVisitor.transformScript(script=pipeline, new_script=new_pipeline)

def extract_files(root_path):
    modes = ["raw-string", "variable", "external"]
    full_paths = {"raw-string": [], "variable": [], "external": []}
    for mode in modes:
        list_files = [f.name for f in os.scandir(f"{root_path}{mode}_python_files") if f.is_file()]

        full_projects = glob(os.path.join(f"{root_path}{mode}/", '**', '*.py'), recursive=True)

        for list_file in list_files:
            for full_file in full_projects:
                if list_file in full_file:
                    full_paths[mode].append(full_file)

        with open(f"{mode}_full_paths.txt", "w") as f:
            for full_path in full_paths[mode]:
                f.write(full_path)
                f.write("\n")
        f.close()


def run_stork(args):
    pipelines = [f.path for f in os.scandir(args.repositories) if f.is_file()]
    print(pipelines)
    output_logger = createLoggerPlain(filename=f"{args.outputs}/paper_example_times.log",
                                      project_name=f"paper_example_outputs",
                                      level=logging.INFO)
    stats = {}
    for pipeline in pipelines:
        pipeline_name = getDatasetName(pipeline.strip())
        logger = createLogger(filename=f"{args.individual_logs}/{pipeline_name}.log",
                              project_name=f"{pipeline_name}_project",
                              level=logging.INFO)
        stork = Stork(logger=logger)

        stork.setup(pipeline=pipeline.strip(), new_pipeline=f"new_{pipeline}.py", destination_path=args.outputs)

        stats[pipeline] = {"translation_time": stork.translation_times,
                           "datasets": {"schema_gen": stork.schema_generation_times},
                           "table_creation": stork.table_creation_times,
                           "table_insertion": stork.table_insertion_times,
                           "data_sizes": stork.dataframe_sizes
                           }
        output_logger.info(f"{pipeline.split('/')[-1].strip()}: {stats[pipeline]}")


def main(args):
    os.makedirs(args.repositories, exist_ok=True)
    os.makedirs(args.individual_logs, exist_ok=True)
    os.makedirs(args.outputs, exist_ok=True)

    run_stork(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Run Stork with a local file system',
    )

    parser.add_argument('-r', '--repositories',
                        default='/home/ilint/HPI/Stork/average-runtime/paper-example/')
    parser.add_argument('-l', '--individual_logs',
                        default='/home/ilint/HPI/Stork/average-runtime/individual_logs/')
    parser.add_argument('-o', '--outputs',
                        default='/home/ilint/HPI/Stork/average-runtime/outputs/')

    args = parser.parse_args()
    main(args)
