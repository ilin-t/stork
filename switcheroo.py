import os
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
    def setup(self, pipeline):

        # self.access_key, self.secret_access_key = self.parseConfig()
        self.setClient(self.access_key, self.secret_access_key)

        self.setPipeline(pipeline=pipeline)

        tree = util.getAst(pipeline=pipeline)
        self.assignVisitor.visit(tree)
        # print(self.assignVisitor.assignments)
        self.assignVisitor.filter_Assignments()
        # print(self.assignVisitor.assignments)
        self.assignVisitor.filter_datasets()
        # print(self.assignVisitor.datasets)

        for member in self.assignVisitor.datasets:
            print(member["variable"])
            for source in member["data_source"]:
                try:
                    if util.checkDataFile(source["data_file"]):
                    # print(os.getcwd())
                        abs_path_dataset = self.parsePath(source["data_file"][0])
                        print(f"Source data file:{source['data_file']}")
                        # print(f"Absolute path: {abs_path_dataset}")
                        self.connector.uploadFile(path=abs_path_dataset, bucket="switcheroo-test-bucket")
                except TypeError as e:
                    print(e)

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
        self.connector.setResource(access_key=access_key, secret_access_key=secret_access_key, resource=resource)

    def parseConfig(self):
        config = ConfigParser()
        config.read(self.config_path)
        credentials = config["credentials"]

        return credentials["aws_access_key_id"], credentials["aws_secret_access_key"]

    def parsePath(self, data_path):

        pipeline_path = os.path.abspath(self.pipeline)
        pipeline_directory = os.path.split(pipeline_path)

        print(pipeline_directory)

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


if __name__ == '__main__':
    print(os.getcwd())
    switcheroo = Switcheroo(r"examples/config.ini")
    # ak, sak = switcheroo.parseConfig()

    # switcheroo.setup("examples/test.py")
    print(os.getcwd())
    # switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/F1-stats-digoc/app.py")
    # switcheroo.setup(pipeline="examples/argus_eyes.py")
    switcheroo.setup(pipeline="/home/ilint/HPI/repos/github-pipelines/github-repos-3000/log-monitoring/test.py")
    util.reportAssign(switcheroo.pipeline, switcheroo.assignVisitor.assignments, "full")
    print(switcheroo.connector.getClient())

    # print("Access key: %s, secret access key: %s" % (ak, sak))
