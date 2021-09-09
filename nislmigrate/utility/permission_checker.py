import ctypes
import os

from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.migration_action import MigrationAction

RESTORE_WITHOUT_FORCE_FLAG_WARNING = """

'restore' will overwrite existing data for the services being restored,
if you are sure you want to delete existing data and restore the
captured data run the command again with the '-f/--force' flag
"""


def is_running_with_elevated_permissions():
    """
    Checks whether the current process is running with elevated (admin) permissions or not.
    :return: True if the current process is running with elevated permissions.
    """
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def verify_elevated_permissions():
    """
    Checks whether the current process is running with elevated (admin)
    permissions or not and raises an error if it is not.
    """
    if not is_running_with_elevated_permissions():
        raise PermissionError('Please run the migration tool with administrator permissions.')


def verify_force_if_restoring(is_force_set: bool, migration_action: MigrationAction):
    """
    Checks whether the current process is running with elevated (admin)
    permissions or not and raises an error if it is not.
    """
    if not is_force_set and migration_action == MigrationAction.RESTORE:
        raise MigrationError(RESTORE_WITHOUT_FORCE_FLAG_WARNING)
