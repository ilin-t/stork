import argparse
import logging
import os

from src.log_modules.log_results import createLogger
from src.stork_s3 import Stork


def main(args):
    os.makedirs("destination-path/", exist_ok=True)
    os.makedirs("logs/", exist_ok=True)

    logger = createLogger(filename=f"logs/example.log",
                          project_name=f"pipelines/example.py",
                          level=logging.INFO)

    stork = Stork(logger=logger, config_path=args.credentials)
    logger.info("Stork has been initialized.")
    stork.setup(pipeline="pipelines/example.py", new_pipeline="destination-path/example_rewritten.py")
    logger.info(f"{stork.pipeline} is set.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Run Stork with a S3 Backend',
    )

    parser.add_argument('-c', '--credentials')

    args = parser.parse_args()
    main(args)