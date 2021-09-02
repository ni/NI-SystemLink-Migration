from nislmigrate.utility import permission_checker
from nislmigrate.logs import logging_setup, migration_error
from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migration_facilitator import MigrationFacilitator


def run_migration_tool():
    """
    The entry point for the NI SystemLink Migration tool.
    """
    try:
        argument_handler = ArgumentHandler()

        logging_verbosity = argument_handler.get_logging_verbosity()
        logging_setup.configure_logging_to_standard_output(logging_verbosity)
        permission_checker.verify_elevated_permissions()

        migration_action = argument_handler.get_migration_action()
        services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
        migration_directory = argument_handler.get_migration_directory()

        facade_factory = FacadeFactory()
        migration_facilitator = MigrationFacilitator(facade_factory)
        migration_facilitator.migrate(services_to_migrate, migration_action, migration_directory)
    except Exception as e:
        migration_error.handle_migration_error(e)
