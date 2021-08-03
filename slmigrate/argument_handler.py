"""Handle passed-in arguments."""

import argparse
from collections import namedtuple

from slmigrate import (
    constants,
    pluginhandler,
)
from slmigrate.migrationaction import MigrationAction


def create_nislmigrate_argument_parser():
    """Set up available command line arguments.

    :return: An ArgumentParser setup to parse input given by the user into the flags the migration tool expects.
    """
    parser = argparse.ArgumentParser(prog="nislmigrate")

    parent_parser = argparse.ArgumentParser(add_help=False)

    for name, plugin in pluginhandler.load_plugins().items():
        add_plugin_arguments(parent_parser, name, plugin)

    parent_parser.add_argument(
        "--" + constants.MIGRATION_ARG,
        "--directory",
        "--folder",
        help="Specify the directory used for migrated data",
        action="store",
        default=constants.default_migration_dir,
    )
    parent_parser.add_argument(
        "--" + constants.SOURCE_DB_ARG,
        "--sourcedb",
        help="The name of the source directory when performing intra-database migration",
        action="store",
        default=constants.SOURCE_DB,
    )

    commands = parser.add_subparsers(dest=constants.MIGRATION_ACTION_FIELD_NAME)
    commands.add_parser(
        constants.CAPTURE_ARG,
        help="capture is used to pull data and settings off SystemLink server",
        parents=[parent_parser],
    )
    commands.add_parser(
        constants.RESTORE_ARG,
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

    return parser


def get_list_of_services_to_capture_or_restore(arguments):
    """
    Generate a list of migration strategies to use during migration, based on the given arguments.

    :param arguments: The arguments to determine the migration action from.
    :return: A list of selected migration actions.
    """
    services_to_migrate = []
    for arg in vars(arguments):
        if (
            getattr(arguments, arg)
            and not (arg == constants.MIGRATION_ACTION_FIELD_NAME)
            and not (arg == constants.SOURCE_DB_ARG)
            and not (arg == constants.MIGRATION_ARG)
        ):
            services_to_migrate.append(pluginhandler.loaded_plugins[arg])
    return services_to_migrate


def determine_migration_action(arguments):
    validate_migration_action(arguments.action)
    if arguments.action == constants.RESTORE_ARG:
        return MigrationAction.RESTORE
    elif arguments.action == constants.CAPTURE_ARG:
        return MigrationAction.CAPTURE

def validate_migration_action(invalid_value: str):
    if invalid_value is None:
        raise ValueError("Migration action not specified. Specify either 'capture' or 'restore'")
    if not invalid_value == constants.RESTORE_ARG and not invalid_value == constants.CAPTURE_ARG:
        raise ValueError("'%s' is not a valid migration action, change it to 'capture' or 'restore'" % invalid_value)

def get_migration_directory_from_arguments(arguments):
    """
    Sets the migration directory path based on the given arguments.

    :param arguments: The arguments to determine the migration directory from.
    :return: None.
    """
    return getattr(arguments, constants.MIGRATION_ARG, constants.default_migration_dir)


def get_migration_source_database_path_from_arguments(arguments):
    """
    Sets the source directory path based on the given arguments.
    :param arguments: The arguments to determine the source directory from.
    :return: None.
    """
    return getattr(arguments, constants.SOURCE_DB_ARG, constants.SOURCE_DB)


def add_plugin_arguments(parser, name, plugin):
    for name in plugin.names:
        parser.add_argument(
            "--" + name,
            help=plugin.help,
            action="store_true",
            dest=name
        )
