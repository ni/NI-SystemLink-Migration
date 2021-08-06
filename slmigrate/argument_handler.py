import argparse

from slmigrate import (
    constants,
    pluginhandler,
)
from slmigrate.migration_action import MigrationAction

CAPTURE_ARGUMENT = "capture"
RESTORE_ARGUMENT = "restore"
SOURCE_DATABASE_ARGUMENT = "sourcedb"
MIGRATION_DIRECTORY_ARGUMENT = "dir"


class ArgumentHandler:
    """
    Processes arguments either from the command line or just a list of arguments and breaks them
    into the properties required by the migration tool.
    """
    parsed_arguments = None

    def __init__(self, arguments=None):
        """
        Creates a new instance of ArgumentHandler
        :param arguments: The list of arguments to process, or None to directly grab CLI arguments.
        """
        argument_parser = self.create_nislmigrate_argument_parser()
        if arguments is None:
            self.parsed_arguments = argument_parser.parse_args()
        else:
            self.parsed_arguments = argument_parser.parse_args(arguments)

    def create_nislmigrate_argument_parser(self):
        """
        Creates an argparse parser that knows how to parse the migration tool's command line arguments.

        :return: The built parser.
        """
        argument_parser = argparse.ArgumentParser(prog="nislmigrate")

        parent_parser = argparse.ArgumentParser(add_help=False)
        self.add_plugin_arguments(parent_parser)
        self.add_additional_flag_options(parent_parser)

        commands = argument_parser.add_subparsers(dest=constants.MIGRATION_ACTION_FIELD_NAME)
        commands.add_parser(
            CAPTURE_ARGUMENT,
            help="capture is used to pull data and settings off SystemLink server",
            parents=[parent_parser],
        )
        commands.add_parser(
            RESTORE_ARGUMENT,
            help="restore is used to push data and settings to a clean SystemLink server. ",
            parents=[parent_parser],
        )
        commands.add_parser(
            constants.thdbbug.arg,
            help=(
                "Migrate tag history data to the correct MongoDB to resolve an issue introduced in"
                "SystemLink 2020R2 when using a remote Mongo instance. Use --sourcedb to specify a"
                "source database. admin is used if none is specified"
            ),
        )
        return argument_parser

    def add_additional_flag_options(self, parent_parser):
        """
        Creates an argparse parser that knows how to parse the migration tool's command line arguments.

        :param parent_parser: The parent parser to add the flags to.
        """
        parent_parser.add_argument(
            "--" + MIGRATION_DIRECTORY_ARGUMENT,
            "--directory",
            "--folder",
            help="Specify the directory used for migrated data",
            action="store",
            default=constants.DEFAULT_MIGRATION_DIRECTORY,
        )
        parent_parser.add_argument(
            "--" + SOURCE_DATABASE_ARGUMENT,
            "--sourcedb",
            help="The name of the source directory when performing intra-database migration",
            action="store",
            default=constants.SOURCE_DB,
        )

    def get_list_of_services_to_capture_or_restore(self):
        """
        Generate a list of migration strategies to use during migration, based on the given arguments.

        :return: A list of selected migration actions.
        """
        services_to_migrate = []
        for arg in vars(self.parsed_arguments):
            if (
                getattr(self.parsed_arguments, arg) and not
                (arg == constants.MIGRATION_ACTION_FIELD_NAME) and not
                (arg == SOURCE_DATABASE_ARGUMENT) and not
                (arg == MIGRATION_DIRECTORY_ARGUMENT)
            ):
                services_to_migrate.append(pluginhandler.loaded_plugins[arg])
        return services_to_migrate

    def determine_migration_action(self):
        """
        Determines whether to capture or restore based on the arguments.

        :return: None.
        """
        if self.parsed_arguments.action == RESTORE_ARGUMENT:
            return MigrationAction.RESTORE
        elif self.parsed_arguments.action == CAPTURE_ARGUMENT:
            return MigrationAction.CAPTURE

    def get_migration_directory(self):
        """
        Gets the migration directory path based on the parsed arguments.

        :return: The migration directory path from the arguments, or the default if none was specified.
        """
        return getattr(self.parsed_arguments, MIGRATION_DIRECTORY_ARGUMENT, constants.DEFAULT_MIGRATION_DIRECTORY)

    def add_plugin_arguments(self, parser):
        """
        Adds expected arguments to the parser for all plugins.
        :param parser: The parser to add the argument flag to.
        :return: None.
        """
        for _, plugin in pluginhandler.load_plugins().items():
            for name in plugin.names:
                parser.add_argument(
                    "--" + name,
                    help=plugin.help,
                    action="store_true",
                    dest=name
                )
