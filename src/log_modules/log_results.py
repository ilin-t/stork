import logging

def createLogger(filename, project_name, level):
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')

    handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)

    logger = logging.getLogger(project_name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

