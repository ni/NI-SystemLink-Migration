import logging
import traceback


class MigrationError(Exception):
    pass


def handle_migration_error(e: Exception):
    log: logging.Logger = logging.getLogger()
    log.error("%s: %s" % (type(e).__name__, e))
    if log.level == logging.DEBUG:
        traceback.print_exc()
<<<<<<< HEAD
=======
        exit(1)


def handle_migration_warning(e: MigrationWarning):
    log: logging.Logger = logging.getLogger()
    log.warning("%s: %s" % (type(e).__name__, e))
>>>>>>> 35b7c660f67eb80f6db179d8436a4045da188dcc
