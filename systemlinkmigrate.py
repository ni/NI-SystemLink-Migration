"""
Generic migration utility for migrating various data and settings between SystemLink servers.

Not all services will be supported. Additional services will be supported over time.
"""

from nislmigrate import permission_checker
from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.file_handler import FileHandler
from nislmigrate.mongo_handler import MongoHandler
from nislmigrate.service_migrator import ServiceMigrator
from nislmigrate.systemlink_service_manager import SystemLinkServiceManager


def main():
    """
    The entry point for the NI SystemLink Migration tool.
    """
    permission_checker.raise_exception_if_not_running_with_elevated_permissions()

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
