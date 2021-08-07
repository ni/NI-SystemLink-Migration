import argparse
import os
from typing import List

import nislmigrate.service_plugins
from nislmigrate.constants import MIGRATION_ACTION_FIELD_NAME
from nislmigrate.migration_action import MigrationAction
from nislmigrate.plugin_loader import PluginLoader
from nislmigrate.service import ServicePlugin

CAPTURE_ARGUMENT = "capture"
RESTORE_ARGUMENT = "restore"
THDBBUG_ARGUMENT = "thdbbug"
SOURCE_DATABASE_ARGUMENT = "sourcedb"
MIGRATION_DIRECTORY_ARGUMENT = "dir"
DEFAULT_MIGRATION_DIRECTORY = os.path.expanduser("~\\Documents\\migration")


class ArgumentHandler:
    """
    Processes arguments either from the command line or just a list of arguments and breaks them
    into the properties required by the migration tool.
    """
    parsed_arguments = None
    plugin_loader = PluginLoader(nislmigrate.service_plugins, ServicePlugin)

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

    def get_list_of_services_to_capture_or_restore(self) -> List[ServicePlugin]:
        """
        Generate a list of migration strategies to use during migration, based on the given arguments.

        :return: A list of selected migration actions.
        """
        services_to_migrate = []
        for arg in vars(self.parsed_arguments):
            if (
                getattr(self.parsed_arguments, arg) and not
                (arg == MIGRATION_ACTION_FIELD_NAME) and not
                (arg == SOURCE_DATABASE_ARGUMENT) and not
                (arg == MIGRATION_DIRECTORY_ARGUMENT)
            ):
                services_to_migrate.append(self.plugin_loader.get_plugins()[arg])
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

    def get_migration_directory(self) -> str:
        """
        Gets the migration directory path based on the parsed arguments.
        :return: The migration directory path from the arguments, or the default if none was specified.
        """
        return getattr(self.parsed_arguments, MIGRATION_DIRECTORY_ARGUMENT, DEFAULT_MIGRATION_DIRECTORY)

    def __create_migration_tool_argument_parser(self) -> argparse.ArgumentParser:
        """
        Creates an argparse parser that knows how to parse the migration tool's command line arguments.
        :return: The built parser.
        """
        argument_parser = argparse.ArgumentParser(prog="nislmigrate")

        parent_parser = argparse.ArgumentParser(add_help=False)
        self.__add_plugin_arguments(parent_parser)
        self.__add_additional_flag_options(parent_parser)

        commands = argument_parser.add_subparsers(dest=MIGRATION_ACTION_FIELD_NAME)
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
            THDBBUG_ARGUMENT,
            help=(
                "Migrate tag history data to the correct MongoDB to resolve an issue introduced in"
                "SystemLink 2020R2 when using a remote Mongo instance. Use --sourcedb to specify a"
                "source database. admin is used if none is specified"
            ),
        )
        return argument_parser

    def __add_additional_flag_options(self, parser: argparse.ArgumentParser) -> None:
        """
        Creates an argparse parser that knows how to parse the migration tool's command line arguments.
        :param parser: The parser to add the flags to.
        """
        parser.add_argument(
            "--" + MIGRATION_DIRECTORY_ARGUMENT,
            "--directory",
            "--folder",
            help="Specify the directory used for migrated data",
            action="store",
            default=DEFAULT_MIGRATION_DIRECTORY,
        )
        parser.add_argument(
            "--" + SOURCE_DATABASE_ARGUMENT,
            "--sourcedb",
            help="The name of the source directory when performing intra-database migration",
            action="store",
            default="admin",
        )

    def __add_plugin_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Adds expected arguments to the parser for all plugins.
        :param parser: The parser to add the argument flag to.
        """
        for _, plugin in self.plugin_loader.get_plugins().items():
            for name in plugin.names:
                parser.add_argument(
                    "--" + name,
                    help=plugin.help,
                    action="store_true",
                    dest=name
                )
