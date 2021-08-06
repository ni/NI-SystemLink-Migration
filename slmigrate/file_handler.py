"""Handle file and directory operations."""

import os
import shutil
import stat
from distutils import dir_util

from slmigrate import constants
from slmigrate.migration_action import MigrationAction
from slmigrate.service import ServicePlugin


class FileHandler:
    """
    Handles operations that act on the real file system.
    """
    def remove_readonly(self, func, path, excinfo):
        """
        Removes the readonly attribute from a file path.

        :param func: A continuation to run with the path.
        :param path: The path to remove the readonly attribute from.
        :param excinfo: Not used.
        :return: None.
        """
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def determine_migration_directory_for_service(self, migration_directory_root: str, service: ServicePlugin):
        """
        Generates the migration directory for a particular service.

        :param service: The service to determine the migration directory for.
        :return: The migration directory for the service.
        """
        return os.path.join(migration_directory_root, service.name)

    def migration_dir_exists(self, dir_):
        """
        Determines whether a directory exists.

        :param dir_: The directory path to check.
        :return: True if the given directory path is a directory and exists.
        """
        return os.path.isdir(dir_)

    def service_restore_singlefile_exists(self, migration_directory_root: str, service: ServicePlugin):
        """
        Checks whether the migrated data for a given single file migration
        service exists in the migration directory and can be restored.

        :param service: The service to verify data has been migrated for.
        :return: True if there is migrated data for a given service
        """
        if not service.config.singlefile_migration:
            return True

        return os.path.isfile(
            os.path.join(self.determine_migration_directory_for_service(migration_directory_root, service), service.config.singlefile_to_migrate)
        )

    def service_restore_dir_exists(self, migration_directory_root: str, service: ServicePlugin):
        """
        Checks whether the migrated data for a given directory migration
        service exists in the migration directory and can be restored.

        :param service: The service to verify data has been migrated for.
        :return: True if there is migrated data for a given service.
        """
        if not service.config.directory_migration:
            return True

        return os.path.isdir(self.determine_migration_directory_for_service(self, migration_directory_root, service))

    def remove_dir(self, dir_):
        """
        Deletes the given directory and its children.

        :param dir_: The directory to remove.
        :return: None.
        """
        if os.path.isdir(dir_):
            shutil.rmtree(dir_, onerror=self.remove_readonly)

    def migrate_singlefile(self, migration_directory_root: str, service: ServicePlugin, action: MigrationAction):
        """
        Perform a capture or restore the given service.

        :param service: The service to capture or restore.
        :param action: Whether to capture or restore.
        :return: None.
        """
        if not service.singlefile_migration:
            return
        migration_dir = self.determine_migration_directory_for_service(migration_directory_root, service)
        if action == MigrationAction.CAPTURE:
            self.remove_dir(migration_dir)
            os.mkdir(migration_dir)
            singlefile_full_path = os.path.join(
                constants.program_data_dir,
                service.singlefile_source_dir,
                service.singlefile_to_migrate,
            )
            shutil.copy(singlefile_full_path, migration_dir)
        elif action == MigrationAction.RESTORE:
            singlefile_full_path = os.path.join(migration_dir, service.singlefile_to_migrate)
            shutil.copy(singlefile_full_path, service.singlefile_source_dir)

    def capture_singlefile(self, migration_directory_root: str, service: ServicePlugin, dir, file):
        migration_dir = self.determine_migration_directory_for_service(migration_directory_root, service)
        self.remove_dir(migration_dir)
        os.mkdir(migration_dir)
        singlefile_full_path = os.path.join(
            constants.program_data_dir,
            dir,
            file,
        )
        shutil.copy(singlefile_full_path, migration_dir)

    def restore_singlefile(self, migration_directory_root: str, service: ServicePlugin, dir, file):
        migration_dir = self.determine_migration_directory_for_service(migration_directory_root, service)
        singlefile_full_path = os.path.join(migration_dir, service.file)
        shutil.copy(singlefile_full_path, dir)

    def migrate_dir(self, migration_directory_root: str, service: ServicePlugin, action: MigrationAction):
        """
        Perform a capture or restore the given service.

        :param service: The service to capture or restore.
        :param action: Whether to capture or restore.
        :return: None.
        """
        if not service.directory_migration:
            return
        migration_dir = self.determine_migration_directory_for_service(migration_directory_root, service)
        if action == MigrationAction.CAPTURE:
            self.remove_dir(migration_dir)
            shutil.copytree(service.source_dir, migration_dir)
        elif action == MigrationAction.RESTORE:
            self.remove_dir(service.source_dir)
            dir_util.copy_tree(migration_dir, service.source_dir)
