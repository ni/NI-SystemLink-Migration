"""Generic migration utility for migrating various data and settings between SystemLink servers.

Not all services will be supported. Additional services will be supported over time.
"""

import ctypes, os

from slmigrate import (
    argument_handler,
    constants,
    filehandler,
    servicemgrhandler,
    servicemigrator,
)

from slmigrate.ServiceMigrationSpecification import ServiceMigrationSpecification
from slmigrate.MigrationAction import MigrationAction

# Main
from slmigrate.mongohandler import MongoHandler

def is_admin():
    try:
        return (os.getuid() == 0)
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def main():
    """
    The entry point for the NI SystemLink Migration tool.

    :return: None.
    """
    if not is_admin():
        report_error("Please run the migration tool with administrator permissions.")
    try:
        argument_parser = argument_handler.create_nislmigrate_argument_parser()
        parsed_arguments = argument_parser.parse_args()
        constants.SOURCE_DB = argument_handler.get_migration_source_database_path_from_arguments(parsed_arguments)

        migrator = servicemigrator.ServiceMigrator()
        migrator.mongo_handler = MongoHandler()
        migrator.file_handler = filehandler
        migrator.service_manager = servicemgrhandler

        services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore(parsed_arguments)
        migration_action = argument_handler.determine_migration_action(parsed_arguments)
        migration_directory = argument_handler.get_migration_directory_from_arguments(parsed_arguments)

        migrator.migrate_services(services_to_migrate, migration_action, migration_directory)
    except Exception as exception:
        argument_parser.error(str(exception))

if __name__ == "__main__":
    main()
