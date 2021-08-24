"""
Generic migration utility for migrating various data and settings between SystemLink servers.

Not all services will be supported. Additional services will be supported over time.
"""
from nislmigrate import permission_checker, logging_setup, migration_error
from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.migration_facilitator import MigrationFacilitator
from nislmigrate.systemlink_service_manager import SystemLinkServiceManager


def run_migration_tool():
    """
    The entry point for the NI SystemLink Migration tool.
    """
    try:
        argument_handler = ArgumentHandler()

        logging_verbosity = argument_handler.get_logging_verbosity()
        logging_setup.configure_logging_to_standard_output(logging_verbosity)
        permission_checker.verify_elevated_permissions()

        migration_action = argument_handler.determine_migration_action()
        services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
        migration_directory = argument_handler.get_migration_directory()

        migrator_factory = FacadeFactory()
        migrator_factory.mongo_facade = MongoFacade()
        migrator_factory.file_system_facade = FileSystemFacade()

        service_manager = SystemLinkServiceManager()
        migration_facilitator = MigrationFacilitator(migrator_factory, service_manager)
        migration_facilitator.migrate(services_to_migrate, migration_action, migration_directory)
    except Exception as e:
        migration_error.handle_migration_error(e)
