import os
import boto3

from ast_playground import AssignVisitor
from util import getAst


class S3Connector:
    def __init__(self):
        self.client = None
        self.connection = None
        self.resource = None
        self.pipeline = ""
        self.ast = ""

    def setClient(self, aws_access_key, aws_secret_access_key, client="s3"):
        self.client = boto3.client(service_name=client, aws_access_key_id=aws_access_key,
                                   aws_secret_access_key=aws_secret_access_key)

    # def setConnection(self):
    #     self.connection = []

    def setResource(self, aws_access_key, aws_secret_access_key, resource):
        self.resource = boto3.resource(aws_access_key, aws_secret_access_key, resource)

    def setPipeline(self, pipeline):
        self.pipeline = pipeline

    def getClient(self):
        return self.client

    # def getConnection(self):
    #     return self.connection

    def getResource(self):
        return self.resource

    def setAst(self):
        self.ast = getAst(self.pipeline)

    def uploadFile(self, path, bucket="switcheroo-test-bucket"):
        filename = os.path.split(path)[1]
        self.client.upload_file(
            Filename=path,
            Bucket=bucket,
            Key=filename
        )

    @staticmethod
    def getObjectUrl(key, bucket="switcheroo-test-bucket"):
        return f'https://{bucket}.s3.amazonaws.com/{key}'

    def downloadFile(self, key, bucket="switcheroo-test-bucket"):
        self.client.download_file(
            Filename=key,
            Bucket=bucket,
            Key=key
        )

    def getBuckets(self):
        for bucket in self.resource.buckets.all():
            print(bucket.name)
