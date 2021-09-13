import logging
import os

from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.ni_web_server_manager_facade import NiWebServerManagerFacade
from nislmigrate.migration_action import MigrationAction
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade
from nislmigrate.utility import permission_checker


class MigrationFacilitator:
    """
    Facilitates an entire capture or restore operation from start to finish.
    """
    def __init__(self, facade_factory: FacadeFactory, argument_handler: ArgumentHandler):
        self.facade_factory: FacadeFactory = facade_factory
        self.web_server_manager: NiWebServerManagerFacade = facade_factory.get_ni_web_server_manager_facade()
        self.service_manager: SystemLinkServiceManagerFacade = facade_factory.get_system_link_service_manager_facade()

        self._action = argument_handler.get_migration_action()
        self._migrators = argument_handler.get_list_of_services_to_capture_or_restore()
        self._migration_directory = argument_handler.get_migration_directory()
        self._argument_handler = argument_handler

    def migrate(self):
        """Facilitates an entire capture or restore operation from start to finish.
        """

        self.__pre_migration_error_check()
        self.__stop_services_and_perform_migration()

    def __stop_services_and_perform_migration(self) -> None:
        self.service_manager.stop_all_system_link_services()
        try:
            for migrator in self._migrators:
                migrator_directory = os.path.join(self._migration_directory, migrator.name)
                self.__report_migration_starting(migrator.name)
                self.__migrate_service(migrator, migrator_directory)
                self.__report_migration_finished(migrator.name)
        finally:
            if self._action == MigrationAction.RESTORE:
                self.web_server_manager.restart_web_server()
            self.service_manager.start_all_system_link_services()

    def __migrate_service(self, migrator: MigratorPlugin, migrator_directory) -> None:
        migrator_arguments = self._argument_handler.get_migrator_additional_arguments(migrator)
        if self._action == MigrationAction.CAPTURE:
            migrator.capture(migrator_directory, self.facade_factory, migrator_arguments)
        elif self._action == MigrationAction.RESTORE:
            migrator.restore(migrator_directory, self.facade_factory, migrator_arguments)
        else:
            raise ValueError('Migration action is not the correct type.')

    def __report_migration_starting(self, migrator_name: str):
        action_pretty_name = 'capture' if self._action == MigrationAction.CAPTURE else 'restore'
        migrator_names = (action_pretty_name, migrator_name)
        info = f'Starting to {action_pretty_name} data using {migrator_names} migrator strategy ...'
        log = logging.getLogger(MigrationFacilitator.__name__)
        log.log(logging.INFO, info)

    def __report_migration_finished(self, migrator_name: str):
        action_pretty_name = 'capturing' if self._action == MigrationAction.CAPTURE else 'restoring'
        info = f'Done {action_pretty_name} data using {migrator_name} migrator strategy.'
        log = logging.getLogger(MigrationFacilitator.__name__)
        log.log(logging.INFO, info)

    def __pre_migration_error_check(self) -> None:
        is_force_migration_flag_present = self._argument_handler.is_force_migration_flag_present()
        permission_checker.verify_force_if_restoring(is_force_migration_flag_present, self._action)

        migrator: MigratorPlugin
        for migrator in self._migrators:
            migrator_directory = os.path.join(self._migration_directory, migrator.name)
            arguments = self._argument_handler.get_migrator_additional_arguments(migrator)
            if self._action == MigrationAction.CAPTURE:
                migrator.pre_capture_check(migrator_directory, self.facade_factory, arguments)
            elif self._action == MigrationAction.RESTORE:
                migrator.pre_restore_check(migrator_directory, self.facade_factory, arguments)
            else:
                raise ValueError('Migration action is not the correct type.')
