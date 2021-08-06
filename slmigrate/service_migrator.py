from slmigrate.migration_action import MigrationAction
from slmigrate.service import ServicePlugin


class ServiceMigrator:
    migration_directory = ""
    migration_strategies = []
    mongo_handler = None
    file_handler = None
    service_manager = None

    def migrate_services(self, service_migrators: list, migration_action: MigrationAction, migration_directory: str):
        self.pre_migration_error_check(service_migrators, migration_directory)
        self.stop_services_and_perform_migration(service_migrators, migration_action)

    def stop_services_and_perform_migration(self, service_migrators: list, action: MigrationAction):
        self.service_manager.stop_all_sl_services()
        self.mongo_handler.start_mongo()

        for migrator in service_migrators:
            self.migrate_service(migrator, action)

        self.mongo_handler.stop_mongo()
        self.service_manager.start_all_sl_services()

    def migrate_service(self, migrator: ServicePlugin, action: MigrationAction):
        print(migrator.name + " " + str(action) + " migration called")
        if action == MigrationAction.CAPTURE:
            migrator.capture(self.mongo_handler, self.file_handler)
        elif action == MigrationAction.RESTORE:
            migrator.restore(self.mongo_handler, self.file_handler)
        else:
            raise ValueError("Migration action is not the correct type.")

    def pre_migration_error_check(self, migrators: list, migration_directory: str):
        for migrator in migrators:
            migrator.restore_error_check(migration_directory, self.mongo_handler, self.file_handler)
