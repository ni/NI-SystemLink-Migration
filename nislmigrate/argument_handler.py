import argparse
import logging
import os
from typing import List

from nislmigrate.migration_action import MigrationAction
from nislmigrate import migrators
from nislmigrate.logging.migration_error import MigrationError
from nislmigrate.extensibility.migrator_plugin_loader import MigratorPluginLoader
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin

PROGRAM_NAME = "nislmigrate"
CAPTURE_ARGUMENT = "capture"
RESTORE_ARGUMENT = "restore"
ALL_SERVICES_ARGUMENT = "all"
MIGRATION_DIRECTORY_ARGUMENT = "dir"
DEFAULT_MIGRATION_DIRECTORY = os.path.expanduser("~\\Documents\\migration")
MIGRATION_ACTION_FIELD_NAME = "action"

NO_SERVICES_SPECIFIED_ERROR_TEXT = """
Must specify at least one service to migrate, or migrate all services with the `--all` flag.

Run `nislmigrate capture/restore --help` to list all supported services."""

CAPTURE_OR_RESTORE_NOT_PROVIDED_ERROR_TEXT = """
The 'capture' or 'restore' argument must be provided."""


class ArgumentHandler:
    """
    Processes arguments either from the command line or just a list of arguments and breaks them
    into the properties required by the migration tool.
    """
    parsed_arguments: argparse.Namespace = None
    plugin_loader: MigratorPluginLoader = MigratorPluginLoader(migrators, MigratorPlugin)

    def __init__(self,  arguments: List[str] = None):
        """
        Creates a new instance of ArgumentHandler
        :param arguments: The list of arguments to process, or None to directly grab CLI arguments.
        """
        argument_parser = self.__create_migration_tool_argument_parser()
        if arguments is None:
            self.parsed_arguments = argument_parser.parse_args()
        else:
            self.parsed_arguments = argument_parser.parse_args(arguments)

    def validate_arguments(self):
        pass

    def get_list_of_services_to_capture_or_restore(self) -> List[MigratorPlugin]:
        """
        Generate a list of migration strategies to use during migration,
        based on the given arguments.

        :return: A list of selected migration actions.
        """
        services_to_migrate = []
        for arg in vars(self.parsed_arguments):
            if (
                getattr(self.parsed_arguments, arg) and not
                (arg == MIGRATION_ACTION_FIELD_NAME) and not
                (arg == MIGRATION_DIRECTORY_ARGUMENT)
            ):
                plugin_list = self.plugin_loader.get_plugins().items()
                if arg == ALL_SERVICES_ARGUMENT:
                    services_to_migrate = []
                    for _, plugin in plugin_list:
                        services_to_migrate.append(plugin)
                    return services_to_migrate
                for _, plugin in plugin_list:
                    if arg == plugin.argument and plugin not in services_to_migrate:
                        services_to_migrate.append(plugin)

        if len(services_to_migrate) == 0:
            raise MigrationError(NO_SERVICES_SPECIFIED_ERROR_TEXT)
        return services_to_migrate

    def determine_migration_action(self) -> MigrationAction:
        """
        Determines whether to capture or restore based on the arguments.
        :return: MigrationAction.RESTORE or MigrationAction.CAPTURE.
        """
        if self.parsed_arguments.action == RESTORE_ARGUMENT:
            return MigrationAction.RESTORE
        elif self.parsed_arguments.action == CAPTURE_ARGUMENT:
            return MigrationAction.CAPTURE
        else:
            raise MigrationError(CAPTURE_OR_RESTORE_NOT_PROVIDED_ERROR_TEXT)

    def get_migration_directory(self) -> str:
        """
        Gets the migration directory path based on the parsed arguments.
        :return: The migration directory path from the arguments,
                 or the default if none was specified.
        """
        argument = MIGRATION_DIRECTORY_ARGUMENT
        default = DEFAULT_MIGRATION_DIRECTORY
        return getattr(self.parsed_arguments, argument, default)

    def get_logging_verbosity(self):
        """
        Gets the level with which to logged based on the parsed command line arguments.
        """
        return self.parsed_arguments.verbosity

    def __create_migration_tool_argument_parser(self) -> argparse.ArgumentParser:
        """
        Creates an argparse parser that knows how to parse the migration
        tool's command line arguments.
        :return: The built parser.
        """
        argument_parser = argparse.ArgumentParser(prog=PROGRAM_NAME)
        self.__add_all_flag_options(argument_parser)
        self.__add_capture_and_restore_commands(argument_parser)
        return argument_parser

    def __add_capture_and_restore_commands(self, argument_parser):
        parent_parser = argparse.ArgumentParser(add_help=False)
        self.__add_all_flag_options(parent_parser)
        sub_parser = argument_parser.add_subparsers(
            dest=MIGRATION_ACTION_FIELD_NAME)
        sub_parser.add_parser(
            CAPTURE_ARGUMENT,
            help="capture is used to pull data and settings off SystemLink server",
            parents=[parent_parser])
        sub_parser.add_parser(
            RESTORE_ARGUMENT,
            help="restore is used to push data and settings to a clean SystemLink server. ",
            parents=[parent_parser])

    def __add_all_flag_options(self, argument_parser):
        self.__add_logging_flag_options(argument_parser)
        self.__add_additional_flag_options(argument_parser)
        self.__add_plugin_arguments(argument_parser)

    @staticmethod
    def __add_additional_flag_options(parser: argparse.ArgumentParser) -> None:
        """
        Creates an argparse parser that knows how to parse the migration
        tool's command line arguments.
        :param parser: The parser to add the flags to.
        """
        parser.add_argument(
            "--" + MIGRATION_DIRECTORY_ARGUMENT,
            help="specify the directory used for migrated data (defaults to documents)",
            action="store",
            default=DEFAULT_MIGRATION_DIRECTORY,
        )
        parser.add_argument(
            "--" + ALL_SERVICES_ARGUMENT,
            help="use all provided migrator plugins during a capture or restore operation.",
            action="store_true",
            dest=ALL_SERVICES_ARGUMENT
        )

    @staticmethod
    def __add_logging_flag_options(parser: argparse.ArgumentParser):
        parser.add_argument(
            '-d', '--debug',
            help="print all logged information.",
            action="store_const", dest="verbosity", const=logging.DEBUG,
            default=logging.WARNING,
        )
        parser.add_argument(
            '-v', '--verbose',
            help="print all logged information except debugging information.",
            action="store_const", dest="verbosity", const=logging.INFO,
        )

    def __add_plugin_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Adds expected arguments to the parser for all migrators.
        :param parser: The parser to add the argument flag to.
        """
        for _, plugin in self.plugin_loader.get_plugins().items():
            parser.add_argument(
                "--" + plugin.argument,
                help=plugin.help,
                action="store_true",
                dest=plugin.argument)
