import logging
import os

from src.log_modules.log_results import createLogger
from src.stork_fs import Stork


def main():
    os.makedirs("logs/", exist_ok=True)
    logger = createLogger(filename=f"logs/example.log",
                          project_name=f"pipelines/example.py",
                          level=logging.INFO)

    stork = Stork(logger=logger)
    logger.info("Stork has been initialized.")
    stork.setPipeline(pipeline="pipelines/example.py")
    logger.info(f"{stork.pipeline} is set.")


if __name__ == '__main__':
    main()