"""Generic migration utility for migrating various data and settings between SystemLink servers.

Not all services will be supported. Additional services will be supported over time.
"""

import ctypes
import os

from slmigrate.argument_handler import ArgumentHandler
from slmigrate.file_handler import FileHandler
from slmigrate.mongo_handler import MongoHandler
from slmigrate.service_migrator import ServiceMigrator
from slmigrate.systemlink_service_manager import SystemLinkServiceManager


def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def main():
    """
    The entry point for the NI SystemLink Migration tool.

    :return: None.
    """
    if not is_admin():
        raise PermissionError("Please run the migration tool with administrator permissions.")

    argument_handler = ArgumentHandler()
    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
    migration_action = argument_handler.determine_migration_action()
    migration_directory = argument_handler.get_migration_directory()

    migrator = ServiceMigrator()
    migrator.mongo_handler = MongoHandler()
    migrator.file_handler = FileHandler()
    migrator.service_manager = SystemLinkServiceManager()
    migrator.migrate_services(services_to_migrate, migration_action, migration_directory)


if __name__ == "__main__":
    main()
