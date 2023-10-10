from configparser import ConfigParser
from src.stork_main import Stork


def parseConfig(config_path):
    config = ConfigParser()
    config.read(config_path)
    credentials = config['credentials']
    print(credentials)
    return credentials["aws_access_key_id"], credentials["aws_secret_access_key"]


config_parsed = parseConfig(config_path="config_s3.ini")




