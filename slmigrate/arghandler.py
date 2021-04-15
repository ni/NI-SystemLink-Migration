import argparse
from collections import namedtuple
from slmigrate import constants


# Setup available command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(prog='slmigrate')

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--" + constants.tag.arg, "--tags", "--tagingestion", "--taghistory", help="Migrate tags and tag histories", action="store_true", )
    parent_parser.add_argument("--" + constants.opc.arg, "--opcua", "--opcuaclient", help="Migrate OPCUA sessions and certificates", action="store_true")
    parent_parser.add_argument("--" + constants.fis.arg, "--file", "--files", help="Migrate ingested files", action="store_true")
    parent_parser.add_argument("--" + constants.testmonitor.arg, "--test", "--tests", "--testmonitor", help="Migrate Test Monitor data", action="store_true")
    parent_parser.add_argument("--" + constants.asset.arg, "--assets", help="Migrate asset utilitization and calibration data", action="store_true")
    parent_parser.add_argument("--" + constants.repository.arg, "--repo", help="Migrate packages and feeds", action="store_true")
    parent_parser.add_argument("--" + constants.alarmrule.arg, "--alarms", "--alarm", help="Migrate Tag alarm_rules", action="store_true")
    parent_parser.add_argument("--" + constants.userdata.arg, "--ud", help="Migrate user data", action="store_true")
    parent_parser.add_argument("--" + constants.notification.arg, "--notifications", help="Migrate notifications strategies, templates, and groups", action="store_true")
    parent_parser.add_argument("--" + constants.states.arg, "--state", help="Migrate system states", action="store_true")
    parent_parser.add_argument("--" + constants.migration_arg, "--directory", "--folder", help="Specify the directory used for migrated data", action="store", default=constants.migration_dir)
    parent_parser.add_argument("--" + constants.source_db_arg, "--sourcedb", help="The name of the source directory when performing intra-databse migration", action="store", default=constants.source_db)

    commands = parser.add_subparsers(dest=constants.subparser_storage_attr)
    commands.add_parser(constants.capture_arg, help="capture is used to pull data and settings off SystemLink server", parents=[parent_parser])
    commands.add_parser(constants.restore_arg, help="restore is used to push data and settings to a clean SystemLink server. ", parents=[parent_parser])

    commands.add_parser(constants.thdbbug.arg, help="Migrate tag history data to the correct MongoDB to resolve an issue introduced in SystemLink 2020R2 when using a remote Mongo instance. Use --sourcedb to specify a source database. admin is used if none is specfied",)

    return parser


def determine_migrate_action(arguments):
    ServiceToMigrate = namedtuple('ServiceToMigrate', ['service', 'action'])
    services_to_migrate = []
    for arg in vars(arguments):
        if (getattr(arguments, arg) and not (arg == constants.subparser_storage_attr) and not (arg == constants.source_db_arg) and not (arg == constants.migration_arg)):
            services_to_migrate.append(ServiceToMigrate(service=getattr(constants, arg), action=arguments.action))
    # Special case for thdbbug, since there are no services given on the command line.
    if arguments.action == constants.thdbbug.arg:
        services_to_migrate.append(ServiceToMigrate(service=constants.tag, action=arguments.action))
    return services_to_migrate


def determine_migration_dir(arguments):
    constants.migration_dir = getattr(arguments, constants.migration_arg)


def determine_source_db(arguments):
    constants.source_db = getattr(arguments, constants.source_db_arg)
