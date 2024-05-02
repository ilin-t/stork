import argparse
import logging
import os
import time

from configparser import ConfigParser

from src.log_modules import util
from src.db_conn.s3_connector import S3Connector
from src.ast.assign_visitor import AssignVisitor, getDatasetName
from src.log_modules.log_results import createLogger, createLoggerPlain


class Stork:

    def __init__(self, config_path, logger, connector="s3"):

        if "s3" in connector:
            self.connector = S3Connector()
            self.connector.set_logger(logger)
        self.assignVisitor = AssignVisitor()
        self.pipeline = ""
        self.config_path = config_path
        self.access_key, self.secret_access_key = self.parseConfig(config_path=self.config_path)
        self.assignments = {}
        self.datasets = {}
        self.datasets_urls = {}
        self.read_methods = {}
        self.datasets_read_methods = {}
        self.translation_times = {}
        self.schema_generation_times = {}
        self.table_creation_times = {}
        self.file_upload = {}
        self.dataframe_sizes = {}

    def setPipeline(self, pipeline):
        self.pipeline = pipeline

    def rewritePipeline(self, pipeline):

        try:
            script_name, file_ending = pipeline.split(".")
            self.assignVisitor.transformScript(pipeline, script_name + "_new." + file_ending)
        except len(pipeline.split(".")) > 2:
            print("Pipeline name has wrong formatting.")

    # TODO Check if working on top Resources is a better option
    def setup(self, pipeline, new_pipeline):

        # self.access_key, self.secret_access_key = self.parseConfig()
        self.setClient(self.access_key, self.secret_access_key)
        # self.setResource(self.access_key, self.secret_access_key)

        self.setPipeline(pipeline=pipeline)
        self.assignVisitor.setPipeline(pipeline=self.pipeline)
        self.assignVisitor.setLoggerConfig("test-reviews.log", "test", logging.INFO)

        translation_start = time.time_ns()
        tree = util.getAst(pipeline=pipeline)
        self.assignVisitor.visit(tree)
        self.assignVisitor.filter_Assignments()
        self.assignVisitor.getDatasetsFromReadMethods()
        self.assignVisitor.replace_variables_in_assignments()
        self.assignVisitor.getDatasetsFromInputs()
        translation_end = time.time_ns() - translation_start

        self.translation_times = translation_end / 1000000
        self.connector.logger.info(f"Translation time: {translation_end / 1000000} ms")

        repo_name = self.assignVisitor.parseRepoName(self.assignVisitor.getRepositoryName())

        create_bucket_start = time.time_ns()
        buckets = self.connector.getBucketNames()
        bucket_name = "stork-storage"
        self.connector.createFolder(folder_name=repo_name, bucket=bucket_name)
        print(f"Adapted repository and bucket name: {repo_name}")
        # if repo_name not in buckets:
        #     self.connector.createBucket(bucket_name=bucket_name, region="eu-central-1")
        #     print(f"Should create bucket: {bucket_name}")
        create_bucket_end = time.time_ns() - create_bucket_start

        self.connector.logger.info(f"Bucket generation for {repo_name}: {create_bucket_end / 1000000} ms")
        self.schema_generation_times = (create_bucket_end / 1000000)
        print(f"Datasets recognized: {len(self.assignVisitor.datasets)}")
        for dataset in self.assignVisitor.datasets:
            abs_path_dataset = self.assignVisitor.parsePath(dataset)
            print(f"Absolute path: {abs_path_dataset}")
            if abs_path_dataset and util.fileExists(abs_path_dataset):
                print(f"Dataset: {dataset}")
                # print(f"Source data file:{abs_path_dataset}")
                dataset_name = getDatasetName(abs_path_dataset)
                # dataset_name = ''.join([i for i in dataset_name if i.isalnum()])
                insert_start = time.time_ns()
                self.connector.uploadFile(path=abs_path_dataset, folder="paper-example",
                                          logger="dataset_logger", bucket=bucket_name)
                insert_end = time.time_ns() - insert_start
                self.file_upload[dataset_name] = (insert_end / 1000000)
                self.connector.logger.info(f"Upload time for {dataset_name}: {insert_end / 1000000}ms")

                # print(f"Url: {self.connector.getObjectUrl(key=dataset_name, folder='test-folder', bucket=bucket_name)}")
                self.assignVisitor.datasets_urls.append({"variable": dataset['variable'], "dataset_name": dataset['dataset'],
                                                         "url": self.connector.getObjectUrl(
                                                             key=dataset_name, folder='paper-example', bucket=bucket_name), "lineno": dataset['lineno']})

                self.assignVisitor.transformScript(script=pipeline, new_script=new_pipeline)





    def setClient(self, access_key, secret_access_key, client="s3"):
        print("Access key id: %s, secret access key: %s, service_name: %s" % (access_key, secret_access_key, client))
        self.connector.setClient(aws_access_key=access_key, aws_secret_access_key=secret_access_key, client=client)

    def setResource(self, access_key, secret_access_key, resource="s3"):
        # print("Access key id: %s, secret access key: %s, service_name: %s" % (access_key, secret_access_key, resource))
        self.connector.setResource(aws_access_key=access_key, aws_secret_access_key=secret_access_key,
                                   resource=resource)

    def parseConfig(self, config_path):
        config = ConfigParser()
        config.read(config_path)
        credentials = config['credentials']

        return credentials["aws_access_key_id"], credentials["aws_secret_access_key"]


def get_repository_list(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    f.close()

    return lines




def run_stork(args):
    # pipelines = get_repository_list(f"{args.repositories}/{args.mode}_full_paths.txt")
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
        stork = Stork(logger=logger, config_path=args.credentials)

        stork.setup(pipeline=pipeline.strip(), new_pipeline=f"{pipeline[:-3]}_rewritten.py")

        stats[pipeline] = {"translation_time": stork.translation_times,
                           "datasets": {"schema_gen": stork.schema_generation_times},
                           "table_creation": stork.table_creation_times,
                           "file_upload": stork.file_upload,
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
        prog='Run Stork with a S3 Backend',
    )

    parser.add_argument('-r', '--repositories',
                        default='/home/ilint/HPI/Stork/average-runtime/paper-example/')
    parser.add_argument('-c', '--credentials')
    parser.add_argument('-l', '--individual_logs',
                        default='/home/ilint/HPI/Stork/average-runtime/individual_logs/')
    parser.add_argument('-o', '--outputs',
                        default='/home/ilint/HPI/Stork/average-runtime/outputs')
    parser.add_argument('-m', '--mode',
                        default='external')

    args = parser.parse_args()
    main(args)