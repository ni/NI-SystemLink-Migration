from nislmigrate.migration_action import MigrationAction
from nislmigrate.migrators.migrator_factory import MigratorFactory
from nislmigrate.service import ServicePlugin


class MigrationFacilitator:
    """
    Facilitates an entire capture or restore operation from start to finish.
    """
    migration_strategies = []
    mongo_handler = None
    migrator_factory = None

    def __init__(self, migrator_factory: MigratorFactory):
        self.migrator_factory = migrator_factory

    def migrate(self,
                service_migrators: list,
                migration_action: MigrationAction,
                migration_directory: str):
        """
        Facilitates an entire capture or restore operation from start to finish.
        :param service_migrators: The list of plugins to involve in the migration.
        :param migration_action: Whether to perform a capture or restore migration.
        :param migration_directory: The directory either capture data to, or restore data from.
        """
        self.__pre_migration_error_check(service_migrators, migration_action, migration_directory)
        self.__stop_services_and_perform_migration(service_migrators,
                                                   migration_action,
                                                   migration_directory)

    def __stop_services_and_perform_migration(self,
                                              service_migrators: list,
                                              action: MigrationAction,
                                              migration_directory: str) -> None:
        self.service_manager.stop_all_systemlink_services()
        try:
            for migrator in service_migrators:
                self.__report_migration_starting(migrator.name, action, migration_directory)
                self.__migrate_service(migrator, action, migration_directory)
                self.__report_migration_finished(migrator.name, action)
        except Exception:
            print("Error occurred while migrating " + migrator.name)
            raise
        finally:
            self.service_manager.start_all_systemlink_services()

    def __migrate_service(self,
                          migrator: ServicePlugin,
                          action: MigrationAction,
                          migration_directory: str) -> None:
        if action == MigrationAction.CAPTURE:
            migrator.capture(migration_directory, self.migrator_factory)
        elif action == MigrationAction.RESTORE:
            migrator.restore(migration_directory, self.migrator_factory)
        else:
            raise ValueError("Migration action is not the correct type.")

    def __report_migration_starting(self,
                                    migrator_name: str,
                                    action: MigrationAction,
                                    migration_directory: str):
        action_pretty_name = "capture" if action == MigrationAction.CAPTURE else "restore"
        migrator_names = (action_pretty_name, migrator_name)
        info = "Starting to %s data using %s migrator strategy ..." % migrator_names
        print(info)
        print("Migration directory set to '{0}'".format(migration_directory))

    def __report_migration_finished(self, migrator_name: str, action: MigrationAction):
        action_pretty_name = "capturing" if action == MigrationAction.CAPTURE else "restoring"
        print("Done {0} data using {1} migrator strategy.".format(action_pretty_name,
                                                                  migrator_name))

    def __pre_migration_error_check(self,
                                    plugins: list,
                                    migration_action: MigrationAction,
                                    migration_directory: str) -> None:
        if migration_action == MigrationAction.RESTORE:
            for plugin in plugins:
                plugin.restore_error_check(migration_directory, self.migrator_factory)
