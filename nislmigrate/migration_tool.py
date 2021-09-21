from nislmigrate.logs import logging_setup, migration_error
from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migration_facilitator import MigrationFacilitator
from nislmigrate.utility import permission_checker


def run_migration_tool(facade_factory: FacadeFactory, argument_handler: ArgumentHandler) -> None:
    """
    Runs the migration.

    :param facade_factory: Factory that produces objects abstracting away operations.
    :param argument_handler: Handler for the command line arguments.
    """

    migration_facilitator = MigrationFacilitator(facade_factory, argument_handler)
    migration_facilitator.migrate()


def main():
    """
    The entry point for the NI SystemLink Migration tool.
    """
    try:
        facade_factory = FacadeFactory()
        argument_handler = ArgumentHandler(facade_factory=facade_factory)

        logging_verbosity = argument_handler.get_logging_verbosity()
        logging_setup.configure_logging_to_standard_output(logging_verbosity)
        permission_checker.verify_elevated_permissions()

        run_migration_tool(facade_factory, argument_handler)
    except Exception as e:
        migration_error.handle_migration_error(e)


if __name__ == '__main__':
    main()
