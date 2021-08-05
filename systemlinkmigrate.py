"""Generic migration utility for migrating various data and settings between SystemLink servers.

Not all services will be supported. Additional services will be supported over time.
"""

import ctypes, os

from slmigrate import (
    constants,
    filehandler,
    servicemgrhandler,
    servicemigrator,
)
from slmigrate.argument_handler import ArgumentHandler
from slmigrate.mongohandler import MongoHandler

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
    main_without_admin_check()

# TODO: Remove this once all tests are proper unit tests or end to end tests.
def main_without_admin_check():
    """
    The entry point for the NI SystemLink Migration tool.

    :return: None.
    """
    argument_handler = ArgumentHandler()
    # TODO: Don't overwrite this constant.
    constants.SOURCE_DB = argument_handler.get_migration_source_database_path_from_arguments()

    migrator = servicemigrator.ServiceMigrator()
    migrator.mongo_handler = MongoHandler()
    migrator.file_handler = filehandler
    migrator.service_manager = servicemgrhandler

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
    migration_action = argument_handler.determine_migration_action()
    migration_directory = argument_handler.get_migration_directory_from_arguments()

    migrator.migrate_services(services_to_migrate, migration_action, migration_directory)

if __name__ == "__main__":
    main()
