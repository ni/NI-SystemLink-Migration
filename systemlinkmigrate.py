"""Generic migration utility for migrating various data and settings between SystemLink servers.

Not all services will be supported. Additional services will be supported over time.
"""

from slmigrate import (
    arghandler,
    constants,
    filehandler,
    mongohandler,
    servicemgrhandler,
)


# Main
def main():
    """
    The entry point for the NI SystemLink Migration tool.

    :return: None.
    """
    argparser = arghandler.setup_arguments()
    arguments = argparser.parse_args()
    print(arguments)
    arghandler.determine_migration_dir(arguments)
    services_to_migrate = arghandler.determine_migrate_action(arguments)
    for service_to_migrate in services_to_migrate:
        try:
            service_to_migrate.service.restore_error_check(mongohandler, filehandler)
        except Exception as ex:
            # raise an error in argparse here
            argparser.error(str(ex))
            pass
    arghandler.determine_source_db(arguments)
    servicemgrhandler.stop_all_sl_services()
    mongo_proc = mongohandler.start_mongo(constants.mongod_exe, constants.mongo_config)
    for service_to_migrate in services_to_migrate:
        service = service_to_migrate.service
        action = service_to_migrate.action
        print(service.name + " " + action + " migration called")
        if action == constants.CAPTURE_ARG:
            service.capture(mongohandler, filehandler)
        elif action == constants.RESTORE_ARG:
            service.restore(mongohandler, filehandler)
        elif action == constants.thdbbug.arg:
            service.thdbbug(mongohandler, filehandler)
    mongohandler.stop_mongo(mongo_proc)
    servicemgrhandler.start_all_sl_services()


if __name__ == "__main__":
    main()
