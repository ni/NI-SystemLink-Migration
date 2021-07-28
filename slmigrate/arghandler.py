"""Handle passed-in arguments."""

import argparse
import os
from collections import namedtuple

from slmigrate import constants
from slmigrate.ServiceMigrationSpecification import ServiceMigrationSpecification
from slmigrate.MigrationAction import MigrationAction


def parse_arguments():
    """Set up available command line arguments.

    :return:
    """
    parser = argparse.ArgumentParser(prog="slmigrate")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--" + constants.tag.arg,
        "--tags",
        "--tagingestion",
        "--taghistory",
        help="Migrate tags and tag histories",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.opc.arg,
        "--opcua",
        "--opcuaclient",
        help="Migrate OPCUA sessions and certificates",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.fis.arg,
        "--file",
        "--files",
        help="Migrate ingested files",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.testmonitor.arg,
        "--test",
        "--tests",
        "--testmonitor",
        help="Migrate Test Monitor data",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.asset.arg,
        "--assets",
        help="Migrate asset utilization and calibration data",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.repository.arg,
        "--repo",
        help="Migrate packages and feeds",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.alarmrule.arg,
        "--alarms",
        "--alarm",
        help="Migrate Tag alarm_rules",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.userdata.arg,
        "--ud",
        help="Migrate user data",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.notification.arg,
        "--notifications",
        help="Migrate notifications strategies, templates, and groups",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.states.arg,
        "--state",
        help="Migrate system states",
        action="store_true",
    )
    parent_parser.add_argument(
        "--" + constants.MIGRATION_ARG,
        "--directory",
        "--folder",
        help="Specify the directory used for migrated data",
        action="store",
        default=constants.migration_dir,
    )
    parent_parser.add_argument(
        "--" + constants.SOURCE_DB_ARG,
        "--sourcedb",
        help="The name of the source directory when performing intra-database migration",
        action="store",
        default=constants.SOURCE_DB,
    )

    commands = parser.add_subparsers(dest=constants.SUBPARSER_STORAGE_ATTR)
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


def determine_migration_specifications(arguments):
    """
    Generate a list of migration strategies to use during migration, based on the given arguments.

    :param arguments: The arguments to determine the migration action from.
    :return: A list of selected migration actions.
    """
    service_arguments = []
    for arg in vars(arguments):
        if (
            getattr(arguments, arg)
            and not (arg == constants.SUBPARSER_STORAGE_ATTR)
            and not (arg == constants.SOURCE_DB_ARG)
            and not (arg == constants.MIGRATION_ARG)
        ):
            service_arguments.append(arg)

    service_migration_specifications = []
    for service_argument in service_arguments:
        service_name = getattr(constants, service_argument)
        service_action = get_migration_action(arguments)
        service_migration_directory = get_migration_dir(arguments)
        service_migration_specification = ServiceMigrationSpecification(service_name, service_action, service_migration_directory)
        service_migration_specifications.append(service_migration_specification)
    
    return service_migration_specifications

def get_migration_dir(arguments):
    """
    Gets the migration directory path based on the given arguments.

    :param arguments: The arguments to determine the migration directory from.
    :return: The migration directory specified in the arguments, or a default if none is provided.
    """
    migration_directory_path = getattr(arguments, constants.MIGRATION_ARG, constants.migration_dir)
    if not os.path.isdir(migration_directory_path):
        os.mkdir(migration_directory_path)
    constants.migration_dir = migration_directory_path
    return constants.migration_dir

def get_migration_action(arguments):
    """
    Determines whether to capture or restore the servers data from the given arguments.

    :param arguments: The arguments to determine the migration action.
    :return: The migration action to take.
    """
    if arguments.action == constants.RESTORE_ARG:
        return MigrationAction.RESTORE
    elif arguments.action == constants.CAPTURE_ARG:
        return MigrationAction.CAPTURE
    else:
        print("Please specify whether to 'capture' or 'restore' data.")
        exit()

def verify_migration_action(arguments):
    """
    Determines whether a capture or restore has been specified in the arguments.

    :param arguments: The arguments to verify specify a migration action.
    :return: True if either a capture or restore have been specified in the arguments.
    """
    if arguments.action == constants.RESTORE_ARG or arguments.action == constants.CAPTURE_ARG:
        return True
    return False


def determine_source_db(arguments):
    """
    Sets the source directory path based on the given arguments.
    :param arguments: The arguments to determine the source directory from.
    :return: None.
    """
    constants.SOURCE_DB = getattr(arguments, constants.SOURCE_DB_ARG, constants.SOURCE_DB)
