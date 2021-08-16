"""
Generic migration utility for migrating various data and settings between SystemLink servers.

Not all services will be supported. Additional services will be supported over time.
"""
from nislmigrate import permission_checker
from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.file_migrator import FileMigrator
from nislmigrate.migration_error import MigrationError
from nislmigrate.migrator_factory import MigratorFactory
from nislmigrate.mongo_migrator import MongoMigrator
from nislmigrate.migration_facilitator import MigrationFacilitator
from nislmigrate.systemlink_service_manager import SystemLinkServiceManager


def main():
    """
    The entry point for the NI SystemLink Migration tool.
    """
    try:
        permission_checker.raise_exception_if_not_running_with_elevated_permissions()

        argument_handler = ArgumentHandler()
        services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
        migration_action = argument_handler.determine_migration_action()
        migration_directory = argument_handler.get_migration_directory()

        migrator_factory = MigratorFactory()
        migrator_factory.mongo_migrator = MongoMigrator()
        migrator_factory.file_migrator = FileMigrator()

        migration_facilitator = MigrationFacilitator(migrator_factory)
        migration_facilitator.service_manager = SystemLinkServiceManager()
        migration_facilitator.migrate(services_to_migrate, migration_action, migration_directory)
    except MigrationError as e:
        print(e)


if __name__ == "__main__":
    main()
