import logging

from src.log_modules.log_results import createLogger
from src.stork_fs import Stork


def main():
    logger = createLogger(filename=f"logs/example.log",
                          project_name=f"pipelines/example.py",
                          level=logging.INFO)

    stork = Stork(logger=logger)
    logger.info("Stork has been initialized.")
    stork.setup(pipeline="pipelines/example.py", new_pipeline="destination-path/example_rewritten.py", destination_path="destination-path/")
    logger.info(f"{stork.pipeline} is set.")

if __name__ == '__main__':
    main()