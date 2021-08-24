import ctypes
import os


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
        raise PermissionError("Please run the migration tool with administrator permissions.")
