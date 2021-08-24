import logging
import sys


def configure_logging_to_standard_output(logging_level: int):
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging_level)
    formatter = logging.Formatter(
        "[%(asctime)s] - %(levelname)s - %(name)s - %(message)s",
        "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
