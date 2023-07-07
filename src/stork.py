import hashlib
import os

from configparser import ConfigParser

from src.log_modules import util
from src.db_conn.s3_connector import S3Connector
from src.db_conn.psqlConnector import PsqlConnector
from src.ast.assign_visitor import AssignVisitor


class Stork:

    def __init__(self, config_path, connector="s3"):

        if "s3" in connector:
            self.connector = S3Connector()
        elif "postgres" in connector:
            self.connector = PsqlConnector()
        # TODO DuckDB - Probably not necessary
        else:
            self.connector = None
        self.assignVisitor = AssignVisitor()
        self.pipeline = ""
        self.config_path = config_path
        self.access_key, self.secret_access_key = self.parseConfig(config_path=self.config_path)

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

        tree = util.getAst(pipeline=pipeline)
        self.assignVisitor.visit(tree)
        self.assignVisitor.filter_Assignments()
        # self.assignVisitor.filter_datasets()

        repo_name = self.assignVisitor.parseRepoName(self.assignVisitor.getRepositoryName())
        buckets = self.connector.getBucketNames()
        bucket_name = repo_name
        print(f"Adapted repository and bucket name: {repo_name}")
        if repo_name not in buckets:
            # self.connector.createBucket(bucket_name=bucket_name, region="eu-central-1")
            print(f"Should create bucket: {bucket_name}")
        # for member in self.assignVisitor.inputs:
        #     print(f"variable: {member['variable']}")
        #     for source in member["data_source"]:
        #         print(f"source: {source}")
        #         try:
        #             # print(f"source['data_file']: {source['data_file']}")
        #             for dataset in source["data_file"]:
        #                 if log_modules.checkFileExtension(dataset):
        #                     print(f"dataset:{dataset}")
        #                     if log_modules.checkDataFile(dataset):
        #
        #                         abs_path_dataset = self.parsePath(dataset)
        #                         print(f"Source data file:{abs_path_dataset}")
        #                         self.connector.uploadFile(path=abs_path_dataset, bucket=bucket_name)
        #                         dataset_name = self.getDatasetName(abs_path_dataset)
        #
        #                         print(f"Url: {self.connector.getObjectUrl(key=dataset_name, bucket=bucket_name)}")
        #                         self.assignVisitor.datasets_urls.append({"dataset_name": dataset,
        #                                                                  "url": self.connector.getObjectUrl(
        #                                                                      key=dataset_name, bucket=bucket_name)})
        #
        #         except TypeError as e:
        #             print(e)
        #
        #         except KeyError as e:
        #             print(e)

        # self.assignVisitor.getDatasetsFromInputs()
        # self.assignVisitor.uploadDatasets(bucket=bucket_name)

        # print(f"Datasets_urls: {self.assignVisitor.datasets_urls}")
        # self.assignVisitor.transformScript(script=pipeline, new_script=new_pipeline)
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
    stork = Stork(r"../src/db_conn/config_s3.ini")

    # ak, sak = stork.parseConfig()

    # stork.setup("examples/test.py")
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/F1-stats-digoc/app.py") - working
    # stork.setup(pipeline="../examples/argus_eyes.py", new_pipeline="new_argus_eyes.py")
    # stork = Stork(config_path=r"../db_conn/config_s3.ini")
    pipeline = "log_modules/variable_path_reading_new.py"
    stork.setup(pipeline = pipeline, new_pipeline="new_variable_path_reading_new.py")
    # stork.setup(pipeline="../examples/argus_eyes.py", new_pipeline="new_argus_eyes.py")
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/log-monitoring/test.py") - working
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/log-monitoring/test.py", new_pipeline="new_test.py")
    # #stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/Air_Quality_Analysis/Data-Scripts/Data_extract.py") - not working #
    # #stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/Covid19Tracker/CV19P Code/Python CorrData/CorrData.py") - adapted
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/affects_in_twitter/DataPreprocessing.py") - working
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/281Hamilton/main.py") - not working - no data
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/Archive_Project/ERHFDA_Cleaning.py") - not working - no data
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/craiglist_crawler/__init__.py") - working - adapted
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/craiglist_crawler/__init__.py")
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/Faculdade-Inteligencia_Artificial/aula2.py") - working (contains other pipelines that are not covered)
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/forest-pypi/forest/forestdata.py", new_pipeline="new_forest_data.py")
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/IJCAI-18/上下文特征提取.py") - not working - no data
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/LIContractValue/ir_nss.py", new_pipeline="new_ir_nss.py") - works
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/LIContractValue/ir_nss.py", new_pipeline="new_ir_nss.py")
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/LOONE/Data.py") - not working - not covered
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/pizzaprediction/classification_nn.py") - working
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/pizzaprediction/classification_nn.py", new_pipeline="new_classification.py")
    util.reportAssign(stork.pipeline, stork.assignVisitor.assignments, "full")
    # print("Access key: %s, secret access key: %s" % (ak, sak))

    # stork.setup(pipeline="examples/argus_eyes.py", new_pipeline="new_argus_eyes.py")
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/F1-stats-digoc/app.py", new_pipeline="new_app.py")
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/affects_in_twitter/DataPreprocessing.py", new_pipeline="new_dp.py")
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/craiglist_crawler/__init__.py", new_pipeline="new_crawler.py")
    # stork.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/pizzaprediction/classification_nn.py", new_pipeline="new_classification.py")
