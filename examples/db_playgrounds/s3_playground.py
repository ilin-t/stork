import boto3

s3_resource = boto3.resource("s3")

for bucket in s3_resource.buckets.all():
    print(bucket.name)

s3_client = boto3.client("s3")
# s3_client.upload_file(
#     Filename="data/dataset-31-credit-g.csv",
#     Bucket="stork-test-bucket",
#     Key="dataset-31-credit-g.csv"
# )

s3_client.download_file(
    Bucket="stork-test-bucket",
    Key="dataset-31-credit-g.csv",
    Filename="downloaded.csv"
)