"""Handle file and directory operations."""

import os
import shutil
import stat
from distutils import dir_util

from slmigrate import constants


def remove_readonly(func, path, excinfo):
    """
    Removes the readonly attribute from a file path.

    :param func: A continuation to run with the path.
    :param path: The path to remove the readonly attribute from.
    :param excinfo: Not used.
    :return: None.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def determine_migration_dir(service):
    """
    Generates the migration directory for a particular service.

    :param service: The service to determine the migration directory for.
    :return: The migration directory for the service.
    """
    return os.path.join(constants.migration_dir, service.name)


def migration_dir_exists(dir_):
    """
    Determines whether a directory exists.

    :param dir_: The directory path to check.
    :return: True if the given directory path is a directory and exists.
    """
    return os.path.isdir(dir_)


def service_restore_singlefile_exists(service):
    """
    Checks whether the migrated data for a given single file migration
    service exists in the migration directory and can be restored.

    :param service: The service to verify data has been migrated for.
    :return: True if there is migrated data for a given service
    """
    if not service.singlefile_migration:
        return True

    return os.path.isfile(
        os.path.join(determine_migration_dir(service), service.singlefile_to_migrate)
    )


def service_restore_dir_exists(service):
    """
    Checks whether the migrated data for a given directory migration
    service exists in the migration directory and can be restored.

    :param service: The service to verify data has been migrated for.
    :return: True if there is migrated data for a given service.
    """
    if not service.directory_migration:
        return True

    return os.path.isdir(determine_migration_dir(service))


def remove_dir(dir_):
    """
    Deletes the given directory and its children.

    :param dir_: The directory to remove.
    :return: None.
    """
    if os.path.isdir(dir_):
        shutil.rmtree(dir_, onerror=remove_readonly)


def migrate_singlefile(service, action):
    """
    Perform a capture or restore the given service.

    :param service: The service to capture or restore.
    :param action: Whether to capture or restore.
    :return: None.
    """
    if not service.singlefile_migration:
        return
    migration_dir = determine_migration_dir(service)
    if action == constants.CAPTURE_ARG:
        remove_dir(migration_dir)
        os.mkdir(migration_dir)
        singlefile_full_path = os.path.join(
            constants.program_data_dir,
            service.singlefile_source_dir,
            service.singlefile_to_migrate,
        )
        shutil.copy(singlefile_full_path, migration_dir)
    elif action == constants.RESTORE_ARG:
        singlefile_full_path = os.path.join(migration_dir, service.singlefile_to_migrate)
        shutil.copy(singlefile_full_path, service.singlefile_source_dir)


def capture_singlefile(service, dir, file):
    migration_dir = determine_migration_dir(service)
    remove_dir(migration_dir)
    os.mkdir(migration_dir)
    singlefile_full_path = os.path.join(
        constants.program_data_dir,
        dir,
        file,
    )
    shutil.copy(singlefile_full_path, migration_dir)


def restore_singlefile(service, dir, file):
    migration_dir = determine_migration_dir(service)
    singlefile_full_path = os.path.join(migration_dir, service.file)
    shutil.copy(singlefile_full_path, dir)


def migrate_dir(service, action):
    """
    Perform a capture or restore the given service.

    :param service: The service to capture or restore.
    :param action: Whether to capture or restore.
    :return: None.
    """
    if not service.directory_migration:
        return
    migration_dir = determine_migration_dir(service)
    if action == constants.CAPTURE_ARG:
        remove_dir(migration_dir)
        shutil.copytree(service.source_dir, migration_dir)
    elif action == constants.RESTORE_ARG:
        remove_dir(service.source_dir)
        dir_util.copy_tree(migration_dir, service.source_dir)
