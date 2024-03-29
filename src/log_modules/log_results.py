import logging


def createLogger(filename, project_name, level):
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')

    handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)

    logger = logging.getLogger(project_name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def createLoggerPlain(filename, project_name, level):
    formatter = logging.Formatter('%(message)s')

    handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)

    logger = logging.getLogger(project_name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def closeLog(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()
