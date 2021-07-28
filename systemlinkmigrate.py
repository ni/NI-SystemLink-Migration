"""Generic migration utility for migrating various data and settings between SystemLink servers.

Not all services will be supported. Additional services will be supported over time.
"""

import ctypes, os

from slmigrate import (
    arghandler,
    constants,
    filehandler,
    mongohandler,
    servicemgrhandler,
)

from slmigrate.ServiceMigrationSpecification import ServiceMigrationSpecification
from slmigrate.MigrationAction import MigrationAction


def restore_error_check(argparser, service_migration_specification: ServiceMigrationSpecification):
    """
    Verifies the arguments given are valid for a backup or restore.

    :param argparser: The argument parser object to validate the arguments for.
    :param service: The service to check the arguments are valid for.
    :param action: The action to validate, either backup or restore.
    :return: None.
    """
    service = service_migration_specification.service_info
    if service_migration_specification.migration_action == MigrationAction.RESTORE:
        if not filehandler.migration_dir_exists(service_migration_specification.migration_directory):
            argparser.error(constants.migration_dir + " does not exist")
        if not filehandler.service_restore_singlefile_exists(service):
            argparser.error(
                service.name
                + ": "
                + os.path.join(
                    filehandler.determine_migration_dir(service),
                    service.singlefile_to_migrate,
                )
                + " does not exist"
            )
        if not filehandler.service_restore_dir_exists(service):
            argparser.error(
                service.name
                + ": "
                + filehandler.determine_migration_dir(service)
                + " does not exist"
            )

def is_admin():
    try:
        return (os.getuid() == 0)
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def report_error(message):
    print("\nError: %s\n" % message)
    print("Type --help for a complete list of arguments.")
    exit()

# Main
def main():
    """
    The entry point for the NI SystemLink Migration tool.

    :return: None.
    """

    print()
    if not is_admin():
        report_error("Please run the migration tool with administrator permissions.")

    argparser = arghandler.parse_arguments()
    arguments = argparser.parse_args()

    if not arghandler.verify_migration_action(arguments):
        report_error("Please specify whether to capture or restore data during this migration by including 'capture' or 'restore' as a command argument")

    service_migration_specifications = arghandler.determine_migration_specifications(arguments)

    if (len(service_migration_specifications) == 0):
        report_error("Please specify at least one service to migrate, or use --all to migrate all services.")

    for service_migration_specification in service_migration_specifications:
        print(str(service_migration_specification))

    # for service_migration_specification in service_migration_specifications:
    # restore_error_check(argparser, service_migration_specification)

    arghandler.determine_source_db(arguments)
    servicemgrhandler.stop_all_sl_services()

    mongo_proc = mongohandler.start_mongo(constants.mongod_exe, constants.mongo_config)
    for service_migration_specification in service_migration_specifications:
        service = service_migration_specification.service_info
        action = service_migration_specification.migration_action
        print(service.name + " " + str(action) + " migration started")
        config = mongohandler.get_service_config(service)
        mongohandler.migrate_mongo_cmd(service, action, config)
        filehandler.migrate_dir(service, action)
        filehandler.migrate_singlefile(service, action)
        print(service.name + " " + str(action) + " migration finished")
    mongohandler.stop_mongo(mongo_proc)
    servicemgrhandler.start_all_sl_services()

if __name__ == "__main__":
    main()
