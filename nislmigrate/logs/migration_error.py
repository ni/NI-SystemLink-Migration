import logging
import traceback


class MigrationError(Exception):
    pass


class MigrationWarning(Exception):
    pass


def handle_migration_error(e: Exception):
    log: logging.Logger = logging.getLogger()
    log.error("%s: %s" % (type(e).__name__, e))
    if log.level == logging.DEBUG:
        traceback.print_exc()
        exit(1)


def handle_migration_warning(e: MigrationWarning):
    log: logging.Logger = logging.getLogger()
    log.warning("%s: %s" % (type(e).__name__, e))
