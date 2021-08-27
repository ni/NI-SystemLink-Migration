import logging
import os
from typing import List

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migration_action import MigrationAction
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade


class MigrationFacilitator:
    """
    Facilitates an entire capture or restore operation from start to finish.
    """
    def __init__(self, facade_factory: FacadeFactory):
        self.facade_factory: FacadeFactory = facade_factory
        self.service_manager: SystemLinkServiceManagerFacade = facade_factory.get_system_link_service_manager_facade()

    def migrate(self, migrators: List[MigratorPlugin], migration_action: MigrationAction, migration_directory: str):
        """Facilitates an entire capture or restore operation from start to finish.

        :param migrators: The list of plugins to involve in the migration.
        :param migration_action: Whether to perform a capture or restore migration.
        :param migration_directory: The directory either capture data to, or restore data from.
        """
        self.__pre_migration_error_check(migrators, migration_action, migration_directory)
        self.__stop_services_and_perform_migration(migrators, migration_action, migration_directory)

    def __stop_services_and_perform_migration(
            self,
            migrators: List[MigratorPlugin],
            action: MigrationAction,
            migration_directory: str,
    ) -> None:
        self.service_manager.stop_all_system_link_services()
        try:
            for migrator in migrators:
                migrator_directory = os.path.join(migration_directory, migrator.name)
                self.__report_migration_starting(migrator.name, action)
                self.__migrate_service(migrator, action, migrator_directory)
                self.__report_migration_finished(migrator.name, action)
        finally:
            self.service_manager.start_all_system_link_services()

    def __migrate_service(
            self,
            migrator: MigratorPlugin,
            action: MigrationAction,
            migration_directory: str
    ) -> None:
        if action == MigrationAction.CAPTURE:
            migrator.capture(migration_directory, self.facade_factory)
        elif action == MigrationAction.RESTORE:
            migrator.restore(migration_directory, self.facade_factory)
        else:
            raise ValueError("Migration action is not the correct type.")

    @staticmethod
    def __report_migration_starting(migrator_name: str, action: MigrationAction):
        action_pretty_name = "capture" if action == MigrationAction.CAPTURE else "restore"
        migrator_names = (action_pretty_name, migrator_name)
        info = f"Starting to %s data using {migrator_names} migrator strategy ..."
        log = logging.getLogger(MigrationFacilitator.__name__)
        log.log(logging.INFO, info)

    @staticmethod
    def __report_migration_finished(migrator_name: str, action: MigrationAction):
        action_pretty_name = "capturing" if action == MigrationAction.CAPTURE else "restoring"
        info = f"Done {action_pretty_name} data using {migrator_name} migrator strategy."
        log = logging.getLogger(MigrationFacilitator.__name__)
        log.log(logging.INFO, info)

    def __pre_migration_error_check(
            self,
            plugins: List[MigratorPlugin],
            migration_action: MigrationAction,
            migration_directory: str
    ) -> None:
        if migration_action == MigrationAction.RESTORE:
            plugin: MigratorPlugin
            for plugin in plugins:
                plugin.pre_restore_check(migration_directory, self.facade_factory)
