"""Handle passed-in arguments."""

import argparse
from collections import namedtuple

from slmigrate import constants


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


def determine_migrate_action(arguments):
    """TODO: Complete documentation.

    :param arguments:
    :return:
    """
    ServiceToMigrate = namedtuple("ServiceToMigrate", ["service", "action"])
    services_to_migrate = []
    for arg in vars(arguments):
        if (
            getattr(arguments, arg)
            and not (arg == constants.SUBPARSER_STORAGE_ATTR)
            and not (arg == constants.SOURCE_DB_ARG)
            and not (arg == constants.MIGRATION_ARG)
        ):
            services_to_migrate.append(
                ServiceToMigrate(service=getattr(constants, arg), action=arguments.action)
            )
    # Special case for thdbbug, since there are no services given on the command line.
    if arguments.action == constants.thdbbug.arg:
        services_to_migrate.append(
            ServiceToMigrate(service=constants.tag, action=arguments.action)
        )
    return services_to_migrate


def determine_migration_dir(arguments):
    """TODO: Complete documentation.

    :param arguments:
    :return:
    """
    constants.migration_dir = getattr(arguments, constants.MIGRATION_ARG)


def determine_source_db(arguments):
    """TODO: Complete documentation.

    :param arguments:
    :return:
    """
    constants.SOURCE_DB = getattr(arguments, constants.SOURCE_DB_ARG)
