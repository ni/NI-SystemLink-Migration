import logging
import sys


def configure_logging_to_standard_output(logging_level: int):
    logger = logging.getLogger()
    logger.name = "SystemLinkMigrationTool"
    logger.setLevel(logging_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging_level)
    simple_formatter = logging.Formatter(
        "[%(asctime)s] %(message)s",
        "%Y-%m-%d %H:%M:%S")
    verbose_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        "%Y-%m-%d %H:%M:%S")
    is_info = logging_level == logging.INFO
    is_debug = logging_level == logging.DEBUG
    formatter = verbose_formatter if is_info or is_debug else simple_formatter
    handler.setFormatter(formatter)
    logger.addHandler(handler)
