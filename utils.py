import logging
from logging import handlers


def setup_logger(name):
    wz = logging.getLogger("werkzeug")

    logger = logging.getLogger(name)
    file_handler = handlers.RotatingFileHandler(
        "logs/service.log", maxBytes=1024 * 1000, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    wz.addHandler(file_handler)
    return logger
