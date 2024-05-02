import os
import boto3

from src.log_modules import util


class S3Connector:
    def __init__(self):
        self.client = None
        self.connection = None
        self.logger = None
        self.pipeline = ""
        self.ast = ""


    def set_logger(self, logger):
        self.logger = logger

    def setClient(self, aws_access_key, aws_secret_access_key, client="s3", region=""):
        self.client = boto3.client(service_name=client, aws_access_key_id=aws_access_key,
                                   aws_secret_access_key=aws_secret_access_key)

    def setPipeline(self, pipeline):
        self.pipeline = pipeline

    def getClient(self):
        return self.client

    def setAst(self):
        self.ast = util.getAst(self.pipeline)

    def createBucket(self, bucket_name, region="eu-central-1"):
        location = {'LocationConstraint': region}
        self.client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)

    def uploadFile(self, path, folder, logger, bucket="stork-storage"):
        filename = os.path.split(path)[1]
        try:
            self.client.upload_file(
                Filename=path,
                Bucket=bucket,
                Key=f"{folder}/{filename}"
            )
            # logger.info(f"File {path} found.")
        except FileNotFoundError as e:
            # logger.info(f"File {path} not found.")
            print(f"Please check whether the requested file exists. {e}")

    @staticmethod
    def getObjectUrl(key, folder, bucket="stork-storage"):
        return f'https://{bucket}.s3.amazonaws.com/{f"{folder}/{key}"}'

    def downloadFile(self, key, bucket="stork-storage"):
        self.client.download_file(
            Filename=key,
            Bucket=bucket,
            Key=key
        )

    def createFolder(self, folder_name, bucket="storage-stork"):
        self.client.put_object(Bucket=bucket, Key=f"{folder_name}/")

    def getBuckets(self):
        return self.client.list_buckets()

    def getBucketNames(self):
        return [bucket['Name'] for bucket in self.getBuckets()['Buckets']]
