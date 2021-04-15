"""Generic migration utility for migrating various data and settings between SystemLink servers.

Not all services will be supported. Additional services will be supported over time.
"""

import os

from slmigrate import (
    arghandler,
    constants,
    filehandler,
    mongohandler,
    servicemgrhandler,
)


def restore_error_check(argparser, service, action):
    """TODO: Complete documentation.

    :param argparser:
    :param service:
    :param action:
    :return:
    """
    if action == constants.RESTORE_ARG:
        if not filehandler.migration_dir_exists(constants.migration_dir):
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


# Main
def main():
    """TODO: Complete documentation.

    :return:
    """
    argparser = arghandler.parse_arguments()
    arguments = argparser.parse_args()
    arghandler.determine_migration_dir(arguments)
    services_to_migrate = arghandler.determine_migrate_action(arguments)
    for service_to_migrate in services_to_migrate:
        restore_error_check(argparser, service_to_migrate.SERVICE, service_to_migrate.action)
    arghandler.determine_source_db(arguments)
    servicemgrhandler.stop_all_sl_services()
    mongo_proc = mongohandler.start_mongo(constants.mongod_exe, constants.mongo_config)
    for service_to_migrate in services_to_migrate:
        service = service_to_migrate.SERVICE
        action = service_to_migrate.action
        print(service.name + " " + action + " migration called")
        config = mongohandler.get_service_config(service)
        mongohandler.migrate_mongo_cmd(service, action, config)
        filehandler.migrate_dir(service, action)
        filehandler.migrate_singlefile(service, action)
    mongohandler.stop_mongo(mongo_proc)
    servicemgrhandler.start_all_sl_services()


if __name__ == "__main__":
    main()
