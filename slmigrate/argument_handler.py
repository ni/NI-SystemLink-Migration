"""Handle passed-in arguments."""

import argparse

from slmigrate import (
    constants,
    pluginhandler,
)
from slmigrate.migrationaction import MigrationAction

"""
TODO: Documentation.
"""
class ArgumentHandler:
    parsed_arguments = None

    """
    TODO: Documentation.
    """
    def __init__(self, arguments=None):
        argument_parser = self.create_nislmigrate_argument_parser()
        if arguments is None:
            self.parsed_arguments = argument_parser.parse_args()
        else:
            self.parsed_arguments = argument_parser.parse_args(arguments)


    def create_nislmigrate_argument_parser(self):
        """
        TODO: Documentation.

        :return: An ArgumentParser setup to parse input given by the user into the flags the migration tool expects.
        """
        argument_parser = argparse.ArgumentParser(prog="nislmigrate")

        parent_parser = argparse.ArgumentParser(add_help=False)

        for name, plugin in pluginhandler.load_plugins().items():
            self.add_plugin_arguments(parent_parser, plugin)

        parent_parser.add_argument(
            "--" + constants.MIGRATION_DIRECTORY_ARGUMENT,
            "--directory",
            "--folder",
            help="Specify the directory used for migrated data",
            action="store",
            default=constants.DEFAULT_MIGRATION_DIRECTORY,
        )
        parent_parser.add_argument(
            "--" + constants.SOURCE_DATABASE_ARGUMENT,
            "--sourcedb",
            help="The name of the source directory when performing intra-database migration",
            action="store",
            default=constants.SOURCE_DB,
        )

        commands = argument_parser.add_subparsers(dest=constants.MIGRATION_ACTION_FIELD_NAME)
        commands.add_parser(
            constants.CAPTURE_ARGUMENT,
            help="capture is used to pull data and settings off SystemLink server",
            parents=[parent_parser],
        )
        commands.add_parser(
            constants.RESTORE_ARGUMENT,
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


    def get_list_of_services_to_capture_or_restore(self):
        """
        Generate a list of migration strategies to use during migration, based on the given arguments.

        :return: A list of selected migration actions.
        """
        services_to_migrate = []
        for arg in vars(self.parsed_arguments):
            if (
                getattr(self.parsed_arguments, arg)
                and not (arg == constants.MIGRATION_ACTION_FIELD_NAME)
                and not (arg == constants.SOURCE_DATABASE_ARGUMENT)
                and not (arg == constants.MIGRATION_DIRECTORY_ARGUMENT)
            ):
                services_to_migrate.append(pluginhandler.loaded_plugins[arg])
        return services_to_migrate


    def determine_migration_action(self):
        """
        Determines whether to capture or restore based on the arguments.

        :return: None.
        """
        if self.parsed_arguments.action == constants.RESTORE_ARGUMENT:
            return MigrationAction.RESTORE
        elif self.parsed_arguments.action == constants.CAPTURE_ARGUMENT:
            return MigrationAction.CAPTURE


    def get_migration_directory_from_arguments(self):
        """
        Sets the migration directory path based on the given arguments.

        :return: None.
        """
        return getattr(self.parsed_arguments, constants.MIGRATION_DIRECTORY_ARGUMENT, constants.DEFAULT_MIGRATION_DIRECTORY)


    def get_migration_source_database_path_from_arguments(self):
        """
        Sets the source directory path based on the given arguments.

        :return: None.
        """
        return getattr(self.parsed_arguments, constants.SOURCE_DATABASE_ARGUMENT, constants.SOURCE_DB)


    def add_plugin_arguments(self, parser, plugin):
        """
        Adds expected arguments to the parser for the plugin.
        :param parser: The parser to add the argument flag to.
        :param plugin: The plugin to add an argument flag for.
        :return: None.
        """
        for name in plugin.names:
            parser.add_argument(
                "--" + name,
                help=plugin.help,
                action="store_true",
                dest=name
            )
