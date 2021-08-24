from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migration_action import MigrationAction
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.systemlink_service_manager import SystemLinkServiceManager


class MigrationFacilitator:
    """
    Facilitates an entire capture or restore operation from start to finish.
    """
    migration_strategies = []

    def __init__(self, facade_factory: FacadeFactory, service_manager: SystemLinkServiceManager):
        self.facade_factory: FacadeFactory = facade_factory
        self.service_manager: SystemLinkServiceManager = service_manager

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
        self.service_manager.stop_all_system_link_services()
        try:
            for migrator in service_migrators:
                try:
                    self.__report_migration_starting(migrator.name, action, migration_directory)
                    self.__migrate_service(migrator, action, migration_directory)
                    self.__report_migration_finished(migrator.name, action)
                except Exception:
                    print("Error occurred while migrating " + migrator.name)
                    raise
        finally:
            self.service_manager.start_all_system_link_services()

    def __migrate_service(self,
                          migrator: MigratorPlugin,
                          action: MigrationAction,
                          migration_directory: str) -> None:
        if action == MigrationAction.CAPTURE:
            migrator.capture(migration_directory, self.facade_factory)
        elif action == MigrationAction.RESTORE:
            migrator.restore(migration_directory, self.facade_factory)
        else:
            raise ValueError("Migration action is not the correct type.")

    @staticmethod
    def __report_migration_starting(migrator_name: str,
                                    action: MigrationAction,
                                    migration_directory: str):
        action_pretty_name = "capture" if action == MigrationAction.CAPTURE else "restore"
        migrator_names = (action_pretty_name, migrator_name)
        info = "Starting to %s data using %s migrator strategy ..." % migrator_names
        print(info)
        print("Migration directory set to '{0}'".format(migration_directory))

    @staticmethod
    def __report_migration_finished(migrator_name: str, action: MigrationAction):
        action_pretty_name = "capturing" if action == MigrationAction.CAPTURE else "restoring"
        print("Done {0} data using {1} migrator strategy.".format(action_pretty_name,
                                                                  migrator_name))

    def __pre_migration_error_check(self,
                                    plugins: list,
                                    migration_action: MigrationAction,
                                    migration_directory: str) -> None:
        if migration_action == MigrationAction.RESTORE:
            plugin: MigratorPlugin
            for plugin in plugins:
                plugin.pre_restore_check(migration_directory, self.facade_factory)
