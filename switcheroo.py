import hashlib
import os
import re
from pathlib import Path
from configparser import ConfigParser

import util
from s3_connector import S3Connector
from assign_visitor import AssignVisitor


class Switcheroo:

    def __init__(self, config_path, connector="s3"):

        if "s3" in connector:
            self.connector = S3Connector()
        elif "postgres" in connector:
            self.connector = None
        # TODO: Postgres connector
        # TODO DuckDB? Probably not necessary
        else:
            self.connector = None
        self.assignVisitor = AssignVisitor()
        self.pipeline = ""
        self.config_path = config_path
        self.access_key, self.secret_access_key = self.parseConfig()

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
        # print(self.assignVisitor.assignments)
        self.assignVisitor.filter_Assignments()
        # print(self.assignVisitor.assignments)
        # self.assignVisitor.filter_datasets()
        # print(self.assignVisitor.datasets)

        repo_name = self.parseRepoName(self.getRepositoryName())
        buckets = [bucket['Name'] for bucket in self.connector.getBuckets()['Buckets']]
        print(buckets)
        # print(self.connector.getBuckets())
        bucket_name = repo_name
        print(f"Adapted repository and bucket name: {repo_name}")
        if repo_name not in buckets:
            self.connector.createBucket(bucket_name=bucket_name, region="eu-central-1")

        for member in self.assignVisitor.inputs:
            print(f"variable: {member['variable']}")
            for source in member["data_source"]:
                print(f"source: {source}")
                try:
                    # print(f"source['data_file']: {source['data_file']}")
                    for dataset in source["data_file"]:
                        if util.checkFileExtension(dataset):
                            print(f"dataset:{dataset}")
                            # if util.checkDataFile(dataset):
                            abs_path_dataset = self.parsePath(dataset)
                            # print(f"Source data file:{abs_path_dataset}")
                            self.connector.uploadFile(path=abs_path_dataset, bucket=bucket_name)
                            dataset_name = self.getDatasetName(abs_path_dataset)
                            self.assignVisitor.datasets_urls.append({"dataset_name": dataset,
                                                                     "url": self.connector.getObjectUrl(
                                                                         key=dataset_name, bucket=bucket_name)})

                except TypeError as e:
                    print(e)

                except KeyError as e:
                    print(e)

                print(f"Datasets_urls: {self.assignVisitor.datasets_urls}")
        self.assignVisitor.transformScript(script=pipeline, new_script=new_pipeline)
        # TODO Check which buckets exist for this user. Whether a new bucket should be created for this
        # for dataset in self.assignVisitor.datasets:
        #     self.connector.uploadFile(path=dataset)
        #     filename = os.path.split(dataset)[1]
        #     self.assignVisitor.inputs.append(self.connector.getObjectUrl(filename))

    #       TODO get the URI for this file, add it as a new input in the assignVisitor.inputs

    # def getAst(self):
    #

    def setClient(self, access_key, secret_access_key, client="s3"):
        print("Access key id: %s, secret access key: %s, service_name: %s" % (access_key, secret_access_key, client))
        self.connector.setClient(aws_access_key=access_key, aws_secret_access_key=secret_access_key, client=client)

    def setResource(self, access_key, secret_access_key, resource="s3"):
        print("Access key id: %s, secret access key: %s, service_name: %s" % (access_key, secret_access_key, resource))
        self.connector.setResource(aws_access_key=access_key, aws_secret_access_key=secret_access_key,
                                   resource=resource)

    def parseConfig(self):
        config = ConfigParser()
        config.read(self.config_path)
        credentials = config["credentials"]

        return credentials["aws_access_key_id"], credentials["aws_secret_access_key"]

    def getRepositoryPath(self):
        pipeline_path = os.path.abspath(self.pipeline)
        pipeline_directory = os.path.split(pipeline_path)

        return pipeline_directory

    def getPipelinePath(self):
        return os.path.dirname(self.pipeline)

    def getRepositoryName(self):
        repository_name = os.path.basename(self.getPipelinePath())
        return repository_name

    def getDatasetName(self, dataset_path):
        dataset_path, dataset_name = os.path.split(dataset_path)
        return dataset_name

    def parsePath(self, data_path):

        pipeline_directory = self.getRepositoryPath()
        print(f"Pipeline directory: {pipeline_directory}")

        if data_path[0] == "/":
            return data_path
        elif data_path[0].isalnum():
            return pipeline_directory[0] + "/" + data_path
        elif data_path[0] == ".":
            if data_path[1] == "/":
                return pipeline_directory[0] + "/" + data_path[2:]
            else:
                parent_dir = Path(pipeline_directory[0]).parent.absolute()
                return str(parent_dir) + "/" + data_path[3:]

    def parseRepoName(self, repo_name):
        print(f"Len repository name: {len(repo_name)}")
        if len(repo_name) > 30:
            repo_name = repo_name[0:29]
            print(len(repo_name))

        bucket_name = re.sub(r'[\W_]+', '-', repo_name) + "-" + str(hashlib.md5(repo_name.encode()).hexdigest())
        print(len(bucket_name))
        return bucket_name.lower()


if __name__ == '__main__':
    switcheroo = Switcheroo(r"examples/config.ini")
    # ak, sak = switcheroo.parseConfig()

    # switcheroo.setup("examples/test.py")
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/F1-stats-digoc/app.py") - working
    # switcheroo.setup(pipeline="examples/argus_eyes.py", new_pipeline="new_argus_eyes.py") - working
    switcheroo.setup(pipeline="examples/argus_eyes.py", new_pipeline="new_argus_eyes.py")
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/log-monitoring/test.py") - working
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/log-monitoring/test.py", new_pipeline="new_test.py")
    # #switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/Air_Quality_Analysis/Data-Scripts/Data_extract.py") - not working #
    # #switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/Covid19Tracker/CV19P Code/Python CorrData/CorrData.py") - adapted
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/affects_in_twitter/DataPreprocessing.py") - working
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/281Hamilton/main.py") - not working - no data
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/Archive_Project/ERHFDA_Cleaning.py") - not working - no data
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/craiglist_crawler/__init__.py") - working - adapted
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/craiglist_crawler/__init__.py")
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/Faculdade-Inteligencia_Artificial/aula2.py") - working (contains other pipelines that are not covered)
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/forest-pypi/forest/forestdata.py") - not working - not covered
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/IJCAI-18/上下文特征提取.py") - not working - no data
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/LIContractValue/ir_nss.py", new_pipeline="new_ir_nss.py") - works
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/LIContractValue/ir_nss.py", new_pipeline="new_ir_nss.py")
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/LOONE/Data.py") - not working - not covered
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/pizzaprediction/classification_nn.py") - working
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/pizzaprediction/classification_nn.py", new_pipeline="new_classification.py")
    # util.reportAssign(switcheroo.pipeline, switcheroo.assignVisitor.assignments, "full")
    # print("Access key: %s, secret access key: %s" % (ak, sak))






    # switcheroo.setup(pipeline="examples/argus_eyes.py", new_pipeline="new_argus_eyes.py")
    switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/F1-stats-digoc/app.py", new_pipeline="new_app.py")
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/affects_in_twitter/DataPreprocessing.py", new_pipeline="new_dp.py")
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/craiglist_crawler/__init__.py", new_pipeline="new_crawler.py")
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/pizzaprediction/classification_nn.py", new_pipeline="new_classification.py")

