from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.ni_web_server_manager_facade import NiWebServerManagerFacade
from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.extensibility.migrator_plugin_loader import MigratorPluginLoader
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.facades.process_facade import ProcessError, ProcessFacade, BackgroundProcess
from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade
from pathlib import Path
from typing import List, Optional, Dict, Any

from nislmigrate.migration_action import MigrationAction


class FakeFacadeFactory(FacadeFactory):
    def __init__(self):
        super().__init__()
        self.process_facade: FakeProcessFacade = FakeProcessFacade()
        self.mongo_facade: FakeMongoFacade = FakeMongoFacade(self.process_facade)
        self.file_system_facade: FakeFileSystemFacade = FakeFileSystemFacade()
        self.ni_web_server_manager_facade: FakeNiWebServerManagerFacade = FakeNiWebServerManagerFacade()
        self.system_link_service_manager_facade: FakeServiceManager = FakeServiceManager()

    def get_mongo_facade(self) -> MongoFacade:
        return self.mongo_facade

    def get_file_system_facade(self) -> FileSystemFacade:
        return self.file_system_facade

    def get_ni_web_server_manager_facade(self) -> NiWebServerManagerFacade:
        return self.ni_web_server_manager_facade

    def get_system_link_service_manager_facade(self) -> SystemLinkServiceManagerFacade:
        return self.system_link_service_manager_facade

    def get_process_facade(self) -> ProcessFacade:
        return self.process_facade


class FakeArgumentHandler(ArgumentHandler):
    def __init__(self, services: List[MigratorPlugin], action: MigrationAction):
        self._services: List[MigratorPlugin] = services
        self._action = action

    def get_list_of_services_to_capture_or_restore(self) -> List[MigratorPlugin]:
        return self._services

    def get_migrator_additional_arguments(self, migrator: MigratorPlugin) -> Dict[str, Any]:
        return {}

    def get_migration_action(self) -> MigrationAction:
        return self._action

    def get_migration_directory(self) -> str:
        return ''

    def is_force_migration_flag_present(self) -> bool:
        return True


class FakeFileSystemFacade(FileSystemFacade):
    def __init__(self):
        self.last_read_json_file_path: Optional[str] = None
        self.last_from_directory: Optional[str] = None
        self.last_to_directory: Optional[str] = None
        self.config = {}
        self.directory_exists = True

    def copy_directory(self, from_directory: str, to_directory: str, force: bool):
        self.last_from_directory = from_directory
        self.last_to_directory = to_directory

    def read_json_file(self, path: str) -> dict:
        self.last_read_json_file_path = path
        return self.config

    def migration_dir_exists(self, dir_):
        return self.directory_exists


class FakeMigratorPluginLoader(MigratorPluginLoader):
    def __init__(self, migrators: List[MigratorPlugin]):
        self.__migrators = migrators

    def get_plugins(self) -> List[MigratorPlugin]:
        return self.__migrators


class FakeMongoFacade(MongoFacade):
    is_mongo_running = True

    def __init__(self, process_facade: Optional[ProcessFacade] = None):
        super().__init__(process_facade or FakeProcessFacade())

    def start_mongo(self):
        self.is_mongo_running = True

    def stop_mongo(self):
        self.is_mongo_running = False

    @staticmethod
    def validate_can_restore_database_from_directory(
            directory: str,
            dump_name: str,
    ) -> None:
        pass


class FakeNiWebServerManagerFacade(NiWebServerManagerFacade):
    restart_count = 0

    def restart_web_server(self):
        self.restart_count = self.restart_count + 1


class FakeProcessFacade(ProcessFacade):
    def __init__(self):
        self.reset()

    def reset(self):
        self.captured: bool = False
        self.restored: bool = False

    def run_process(self, args: List[str]):
        archive_arg = [a for a in args if a.startswith('--archive=')][0]
        if not archive_arg:
            raise ProcessError('missing --archive= argument')

        archive_path = Path(archive_arg.split('=')[1])

        if 'mongodump' in args[0]:
            self.handle_mongo_dump(archive_path)
            self.captured = True
        elif 'mongorestore' in args[0]:
            self.handle_mongo_restore(archive_path)
            self.restored = True
        else:
            raise ProcessError('unknown command')

    def run_background_process(self, args: List[str]) -> BackgroundProcess:
        return NoopBackgroundProcess(args)

    def handle_mongo_dump(self, archive_path: Path):
        """Override this method to add test-specific handling."""
        pass

    def handle_mongo_restore(self, archive_path: Path):
        """Override this method to add test-specific handling."""
        pass


class FakeServiceManager(SystemLinkServiceManagerFacade):
    are_services_running = True
    stop_count = 0
    start_count = 0

    def stop_all_system_link_services(self):
        if self.are_services_running:
            self.stop_count = self.stop_count + 1
            self.are_services_running = False

    def start_all_system_link_services(self):
        if not self.are_services_running:
            self.start_count = self.start_count + 1
            self.are_services_running = True


class NoopBackgroundProcess(BackgroundProcess):
    def __init__(self, arguments: List[str]):
        pass

    def stop(self):
        pass
