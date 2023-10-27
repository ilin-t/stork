import hashlib
import logging
import os

from configparser import ConfigParser

from src.log_modules import util
from src.db_conn.s3_connector import S3Connector
from src.db_conn.psqlConnector import PsqlConnector
from src.ast.assign_visitor import AssignVisitor
from src.log_modules.parse_repos import unzip


class Stork:

    def __init__(self, config_path, connector="s3"):

        if "s3" in connector:
            self.connector = S3Connector()
        elif "postgres" in connector:
            self.connector = PsqlConnector()
        else:
            self.connector = None
        self.assignVisitor = AssignVisitor()
        self.pipeline = ""
        self.config_path = config_path
        self.access_key, self.secret_access_key = self.parseConfig(config_path=self.config_path)
        self.assignments = {}
        self.datasets = {}
        self.datasets_urls = {}
        self.read_methods = {}
        self.datasets_read_methods = {}

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
        self.assignVisitor.setLoggerConfig("test-reviews.log", "test", logging.INFO)

        tree = util.getAst(pipeline=pipeline)
        self.assignVisitor.visit(tree)
        self.assignVisitor.filter_Assignments()
        self.assignVisitor.replace_variables_in_assignments()
        self.assignVisitor.getDatasetsFromInputs()
        self.assignVisitor.getDatasetsFromReadMethods()

        repo_name = self.assignVisitor.parseRepoName(self.assignVisitor.getRepositoryName())
        buckets = self.connector.getBucketNames()
        bucket_name = "stork-storage"
        self.connector.createFolder(folder_name=repo_name, bucket=bucket_name)
        print(f"Adapted repository and bucket name: {repo_name}")
        # if repo_name not in buckets:
        #     self.connector.createBucket(bucket_name=bucket_name, region="eu-central-1")
        #     print(f"Should create bucket: {bucket_name}")

        for member in self.assignVisitor.inputs:
            # print(f"variable: {member['variable']}")
            for source in member["data_source"]:
                print(f"source: {source}")
                try:
                    # print(f"source['data_file']: {source['data_file']}")
                    for dataset in source["data_file"]:
                        if util.checkFileExtension(dataset):
                            print(f"dataset:{dataset}")
                            if util.checkDataFile(dataset):

                                abs_path_dataset = self.assignVisitor.parsePath(dataset)
                                print(f"Source data file:{abs_path_dataset}")
                                self.connector.uploadFile(path=abs_path_dataset, folder="test-folder", bucket=bucket_name)
                                dataset_name = self.assignVisitor.getDatasetName(abs_path_dataset)

                                print(f"Url: {self.connector.getObjectUrl(key=dataset_name, folder='test-folder', bucket=bucket_name)}")
                                self.assignVisitor.datasets_urls.append({"variable": member['variable'], "dataset_name": dataset,
                                                                         "url": self.connector.getObjectUrl(
                                                                             key=dataset_name, folder='test-folder', bucket=bucket_name), "lineno": member['lineno']})

                except (TypeError, KeyError) as e:
                    print(e)

        # self.assignVisitor.getDatasetsFromInputs()
        # self.assignVisitor.uploadDatasets(bucket=bucket_name)

        print(f"Datasets_urls: {self.assignVisitor.datasets_urls}")
        self.assignVisitor.transformScript(script=pipeline, new_script=new_pipeline)
        # TODO Check which buckets exist for this user. Whether a new bucket should be created for this
        # for dataset in self.assignVisitor.datasets:
        #     self.connector.uploadFile(path=dataset)
        #     filename = os.path.split(dataset)[1]
        #     self.assignVisitor.inputs.append(self.connector.getObjectUrl(filename))


    def setClient(self, access_key, secret_access_key, client="s3"):
        # print("Access key id: %s, secret access key: %s, service_name: %s" % (access_key, secret_access_key, client))
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





if __name__ == '__main__':
    # stork = Stork(r"../src/db_conn/config_s3.ini")

    # ak, sak = stork.parseConfig()

    stork = Stork(config_path=r"db_conn/config_s3.ini")
    # repo_path = "/home/ilint/HPI/repos/stork/examples/data/table_ocr.zip"
    # unzip(repo_path=repo_path)
    # pipeline = f"{repo_path[:-4]}/table_ocr-master/Evaluations/Tablebank/evaluation.py"

    pipeline = '/home/ilint/HPI/repos/stork/examples/sample_pipelines/var_retrieval/data_read_test.py'
    # pipeline = "/home/ilint/HPI/repos/pipelines/trial/arguseyes/arguseyes/example_pipelines/amazon-reviews.py"

    stork.setup(pipeline = pipeline, new_pipeline="new_amazon_reviews.py")
    print(stork.assignVisitor.inputs)
    # print(stork.datasets)
    # print(stork.assignments)
    print(stork.assignVisitor.datasets)
    print(stork.assignVisitor.read_methods)
    print(stork.assignVisitor.datasets_read_methods)
    # print(stork.assignVisitor.datasets_urls)
    # print(stork.datasets_urls)
    # print(stork.assignVisitor)
    util.reportAssign(stork.pipeline, stork.assignVisitor.assignments, "full")