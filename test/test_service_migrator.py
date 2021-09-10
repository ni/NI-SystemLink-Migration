from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.facades.ni_web_server_manager_facade import NiWebServerManagerFacade
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade
from nislmigrate.migration_action import MigrationAction
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.facades.process_facade import ProcessFacade
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin, DEFAULT_SERVICE_CONFIGURATION_DIRECTORY
from nislmigrate.migration_facilitator import MigrationFacilitator
from test.test_utilities import FakeMongoFacade
from pathlib import Path
import pytest
from typing import Any, Dict, List, Optional


@pytest.mark.unit
def test_capture_services_with_restore_action_captures_plugin():
    facade_factory = FakeFacadeFactory()
    service = TestMigrator()

    argument_handler = FakeArgumentHandler([service], MigrationAction.CAPTURE)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert service.capture_count == 1


@pytest.mark.unit
def test_capture_services_with_restore_action_restores_plugin():
    facade_factory = FakeFacadeFactory()
    service = TestMigrator()

    argument_handler = FakeArgumentHandler([service], MigrationAction.RESTORE)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert service.restore_count == 1


@pytest.mark.unit
def test_capture_services_with_unknown_action_throws_exception():
    facade_factory = FakeFacadeFactory()
    service = TestMigrator()

    argument_handler = FakeArgumentHandler([service], 'unknown')
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    with pytest.raises(ValueError):
        service_migrator.migrate()


@pytest.mark.unit
def test_migrator_reads_configuration():
    facade_factory = FakeFacadeFactory()
    migrator = TestMigrator()

    actual_config = migrator.config(facade_factory)

    assert actual_config == TestFileSystemFacade.config[migrator.name]


@pytest.mark.unit
def test_migrator_reads_configuration_from_default_location():
    facade_factory = FakeFacadeFactory()
    file_system_facade = facade_factory.get_file_system_facade()
    migrator = TestMigrator()
    expected_configuration_file = str(Path(DEFAULT_SERVICE_CONFIGURATION_DIRECTORY) / f'{migrator.name}.json')

    _ = migrator.config(facade_factory)

    assert expected_configuration_file == file_system_facade.last_read_json_file_path


@pytest.mark.unit
def test_migrator_reads_configuration_from_configured_location():
    facade_factory = FakeFacadeFactory()
    file_system_facade = facade_factory.get_file_system_facade()
    migrator = TestMigrator()
    configured_location = Path('C:') / '/Test' / 'Config' / 'Dir'
    migrator.service_configuration_directory = str(configured_location)
    expected_configuration_file = str(configured_location / f'{migrator.name}.json')

    _ = migrator.config(facade_factory)

    assert expected_configuration_file == file_system_facade.last_read_json_file_path


@pytest.mark.unit
def test_migrate_pre_capture_error_check_called_on_migrator_with_same_migration_directory_as_restore():
    fake_migrator = FakeMigrator()
    facade_factory = FakeFacadeFactory()
    argument_handler = FakeArgumentHandler([fake_migrator], MigrationAction.CAPTURE)
    facilitator = MigrationFacilitator(facade_factory, argument_handler)

    facilitator.migrate()

    assert fake_migrator.pre_capture_migration_directory == fake_migrator.capture_migration_directory
    assert fake_migrator.pre_capture_count == 1
    assert fake_migrator.capture_count == 1


@pytest.mark.unit
def test_migrate_pre_restore_error_check_called_on_migrator_with_same_migration_directory_as_restore():
    fake_migrator = FakeMigrator()
    facade_factory = FakeFacadeFactory()
    argument_handler = FakeArgumentHandler([fake_migrator], MigrationAction.RESTORE)
    facilitator = MigrationFacilitator(facade_factory, argument_handler)

    facilitator.migrate()

    assert fake_migrator.pre_restore_migration_directory == fake_migrator.restore_migration_directory
    assert fake_migrator.pre_restore_count == 1
    assert fake_migrator.restore_count == 1


@pytest.mark.unit
@pytest.mark.parametrize('operation', [
    MigrationAction.CAPTURE,
    MigrationAction.RESTORE
])
def test_migrate_services_stops_running_services(operation: MigrationAction):
    facade_factory = FakeFacadeFactory()
    service = FakeMigrator()

    argument_handler = FakeArgumentHandler([service], operation)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert facade_factory.system_link_service_manager_facade.stop_count == 1


@pytest.mark.unit
@pytest.mark.parametrize('operation', [
    MigrationAction.CAPTURE,
    MigrationAction.RESTORE
])
def test_migrate_services_starts_stopped_services(operation: MigrationAction):
    facade_factory = FakeFacadeFactory()
    service = FakeMigrator()

    argument_handler = FakeArgumentHandler([service], operation)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert facade_factory.system_link_service_manager_facade.start_count == 1
    assert facade_factory.system_link_service_manager_facade.are_services_running


@pytest.mark.unit
def test_migrate_services_with_capture_action_does_not_restart_web_server():
    facade_factory = FakeFacadeFactory()
    service = FakeMigrator()

    argument_handler = FakeArgumentHandler([service], MigrationAction.CAPTURE)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert facade_factory.ni_web_server_manager_facade.restart_count == 0


@pytest.mark.unit
def test_migrate_services_with_restore_action_restarts_web_server():
    facade_factory = FakeFacadeFactory()
    service = FakeMigrator()

    argument_handler = FakeArgumentHandler([service], MigrationAction.RESTORE)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert facade_factory.ni_web_server_manager_facade.restart_count == 1


class FakeMigrator(MigratorPlugin):
    pre_restore_migration_directory: str = ''
    pre_capture_migration_directory: str = ''
    restore_migration_directory: str = ''
    capture_migration_directory: str = ''
    restore_count = 0
    capture_count = 0
    restore_count = 0

    @property
    def help(self):
        return ''

    @property
    def name(self):
        return 'test'

    @property
    def argument(self):
        return 'test'

    def capture(self, mongo_handler=None, file_handler=None, arguments=None):
        self.capture_count += 1

    def restore(self, mongo_handler=None, file_handler=None, arguments=None):
        self.restore_count += 1

    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        pass


class TestNiWebServerManagerFacade(NiWebServerManagerFacade):
    restart_count = 0

    def restart_web_server(self):
        self.restart_count = self.restart_count + 1


class TestSystemLinkServiceManagerFacade(SystemLinkServiceManagerFacade):
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


class TestFileSystemFacade(FileSystemFacade):
    config = {
            'test': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }

    def __init__(self):
        self.last_read_json_file_path: Optional[str] = None

    def read_json_file(self, path):
        self.last_read_json_file_path = path
        return self.config


class FakeFacadeFactory(FacadeFactory):
    def __init__(self):
        super().__init__()
        self.process_facade = ProcessFacade()
        self.mongo_facade: FakeMongoFacade = FakeMongoFacade(self.process_facade)
        self.file_system_facade: TestFileSystemFacade = TestFileSystemFacade()
        self.ni_web_server_manager_facade: TestNiWebServerManagerFacade = TestNiWebServerManagerFacade()
        self.system_link_service_manager_facade: TestSystemLinkServiceManagerFacade = TestSystemLinkServiceManagerFacade()  # noqa: E501

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
