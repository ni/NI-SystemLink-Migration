"""Handle file and directory operations."""

import os
import shutil
import stat
from distutils import dir_util

from slmigrate import constants


def remove_readonly(func, path, excinfo):
    """TODO: Complete documentation.

    :param func:
    :param path:
    :param excinfo:
    :return:
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def determine_migration_dir(service):
    """TODO: Complete documentation.

    :param service:
    :return:
    """
    migration_dir = os.path.join(constants.migration_dir, service.name)
    return migration_dir


def migration_dir_exists(dir_):
    """TODO: Complete documentation.

    :param dir_:
    :return:
    """
    return os.path.isdir(dir_)


def service_restore_singlefile_exists(service):
    """TODO: Complete documentation.

    :param service:
    :return:
    """
    if not service.singlefile_migration:
        return True

    return os.path.isfile(
        os.path.join(determine_migration_dir(service), service.singlefile_to_migrate)
    )


def service_restore_dir_exists(service):
    """TODO: Complete documentation.

    :param service:
    :return:
    """
    if not service.directory_migration:
        return True

    return os.path.isdir(determine_migration_dir(service))


def remove_dir(dir_):
    """TODO: Complete documentation.

    :param dir_:
    :return:
    """
    if os.path.isdir(dir_):
        shutil.rmtree(dir_, onerror=remove_readonly)


def migrate_singlefile(service, action):
    """TODO: Complete documentation.

    :param service:
    :param action:
    :return:
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


def migrate_dir(service, action):
    """TODO: Complete documentation.

    :param service:
    :param action:
    :return:
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
