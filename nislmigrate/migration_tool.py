from nislmigrate.utility import permission_checker
from nislmigrate.logs import logging_setup, migration_error
from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migration_action import MigrationAction
from nislmigrate.migration_facilitator import MigrationFacilitator
from typing import List


def run_migration_tool(
        facade_factory: FacadeFactory,
        services_to_migrate: List[MigratorPlugin],
        migration_action: MigrationAction,
        migration_directory: str) -> None:
    """
    Runs the migration.

    :param services_to_migrate: The migration plugins to run.
    :param migration_action: The action to perform.
    :param migration_directory: The directory where the migrated data is stored.
    """

    migration_facilitator = MigrationFacilitator(facade_factory)
    migration_facilitator.migrate(services_to_migrate, migration_action, migration_directory)


def main():
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
        run_migration_tool(facade_factory, services_to_migrate, migration_action, migration_directory)

    except Exception as e:
        migration_error.handle_migration_error(e)


if __name__ == '__main__':
    main()
