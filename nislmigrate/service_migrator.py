from nislmigrate.migration_action import MigrationAction
from nislmigrate.service import ServicePlugin


class ServiceMigrator:
    """
    Facilitates an entire capture or restore operation from start to finish.
    """
    migration_directory = ""
    migration_strategies = []
    mongo_handler = None
    file_handler = None
    service_manager = None

    def migrate_services(self, service_migrators: list, migration_action: MigrationAction, migration_directory: str):
        """
        Facilitates an entire capture or restore operation from start to finish.
        :param service_migrators: The list of migrators to involve in the migration.
        :param migration_action: Whether to perform a capture or restore migration.
        :param migration_directory: The directory either capture data to, or restore data from.
        """
        self.__pre_migration_error_check(service_migrators, migration_directory)
        self.__stop_services_and_perform_migration(service_migrators, migration_action)

    def __stop_services_and_perform_migration(self, service_migrators: list, action: MigrationAction) -> None:
        self.service_manager.stop_all_sl_services()
        self.mongo_handler.start_mongo()

        for migrator in service_migrators:
            self.__migrate_service(migrator, action)

        self.mongo_handler.stop_mongo()
        self.service_manager.start_all_sl_services()

    def __migrate_service(self, migrator: ServicePlugin, action: MigrationAction) -> None:
        print(migrator.name + " " + str(action) + " migration called")
        if action == MigrationAction.CAPTURE:
            migrator.capture(self.mongo_handler, self.file_handler)
        elif action == MigrationAction.RESTORE:
            migrator.restore(self.mongo_handler, self.file_handler)
        else:
            raise ValueError("Migration action is not the correct type.")

    def __pre_migration_error_check(self, migrators: list, migration_directory: str) -> None:
        for migrator in migrators:
            migrator.restore_error_check(migration_directory, self.mongo_handler, self.file_handler)
