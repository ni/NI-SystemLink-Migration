from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.migration_action import MigrationAction
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin, DEFAULT_SERVICE_CONFIGURATION_DIRECTORY
from nislmigrate.migration_facilitator import MigrationFacilitator
from test.test_utilities import FakeFacadeFactory, FakeArgumentHandler
from pathlib import Path
import pytest
from typing import Any, Dict


CONFIGURATION_FOR_TEST = config = {
        'test': {
            'key1': 'value1',
            'key2': 'value2'
        }
    }


@pytest.mark.unit
def test_migrate_services_with_restore_action_captures_plugin():
    facade_factory = configure_fake_facade_factory()
    service = FakeMigrator()

    argument_handler = FakeArgumentHandler([service], MigrationAction.CAPTURE)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert service.capture_count == 1
    assert service.pre_capture_count == 1


@pytest.mark.unit
def test_migrate_services_with_restore_action_restores_plugin():
    facade_factory = configure_fake_facade_factory()
    service = FakeMigrator()

    argument_handler = FakeArgumentHandler([service], MigrationAction.RESTORE)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert service.restore_count == 1
    assert service.pre_restore_count == 1


@pytest.mark.unit
def test_migrate_services_does_not_call_capture_when_pre_capture_check_fails():
    facade_factory = configure_fake_facade_factory()
    service = FakeMigrator()
    service.fail_pre_check = True

    argument_handler = FakeArgumentHandler([service], MigrationAction.CAPTURE)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    with pytest.raises(RuntimeError):
        service_migrator.migrate()

    assert service.pre_capture_count == 1
    assert service.capture_count == 0


@pytest.mark.unit
def test_migrate_services_does_not_call_restore_when_pre_restore_check_fails():
    facade_factory = configure_fake_facade_factory()
    service = FakeMigrator()
    service.fail_pre_check = True

    argument_handler = FakeArgumentHandler([service], MigrationAction.RESTORE)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    with pytest.raises(RuntimeError):
        service_migrator.migrate()

    assert service.pre_restore_count == 1
    assert service.restore_count == 0


@pytest.mark.unit
def test_migrate_services_with_unknown_action_throws_exception():
    facade_factory = configure_fake_facade_factory()
    service = FakeMigrator()

    argument_handler = FakeArgumentHandler([service], 'unknown')
    with pytest.raises(MigrationError):
        MigrationFacilitator(facade_factory, argument_handler)


@pytest.mark.unit
def test_migrator_reads_configuration():
    facade_factory = configure_fake_facade_factory()
    migrator = FakeMigrator()

    actual_config = migrator.config(facade_factory)

    assert actual_config == CONFIGURATION_FOR_TEST[migrator.name]


@pytest.mark.unit
def test_migrator_reads_configuration_from_default_location():
    facade_factory = configure_fake_facade_factory()
    file_system_facade = facade_factory.get_file_system_facade()
    migrator = FakeMigrator()
    expected_configuration_file = str(Path(DEFAULT_SERVICE_CONFIGURATION_DIRECTORY) / f'{migrator.name}.json')

    _ = migrator.config(facade_factory)

    assert expected_configuration_file == file_system_facade.last_read_json_file_path


@pytest.mark.unit
def test_migrator_reads_configuration_from_configured_location():
    facade_factory = configure_fake_facade_factory()
    file_system_facade = facade_factory.get_file_system_facade()
    migrator = FakeMigrator()
    configured_location = Path('C:') / '/Test' / 'Config' / 'Dir'
    migrator.service_configuration_directory = str(configured_location)
    expected_configuration_file = str(configured_location / f'{migrator.name}.json')

    _ = migrator.config(facade_factory)

    assert expected_configuration_file == file_system_facade.last_read_json_file_path


@pytest.mark.unit
def test_migrate_pre_capture_error_check_called_on_migrator_with_same_migration_directory_as_restore():
    fake_migrator = FakeMigrator()
    facade_factory = configure_fake_facade_factory()
    argument_handler = FakeArgumentHandler([fake_migrator], MigrationAction.CAPTURE)
    facilitator = MigrationFacilitator(facade_factory, argument_handler)

    facilitator.migrate()

    assert fake_migrator.pre_capture_migration_directory == fake_migrator.capture_migration_directory
    assert fake_migrator.pre_capture_count == 1
    assert fake_migrator.capture_count == 1


@pytest.mark.unit
def test_migrate_pre_restore_error_check_called_on_migrator_with_same_migration_directory_as_restore():
    fake_migrator = FakeMigrator()
    facade_factory = configure_fake_facade_factory()
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
    facade_factory = configure_fake_facade_factory()
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
    facade_factory = configure_fake_facade_factory()
    service = FakeMigrator()

    argument_handler = FakeArgumentHandler([service], operation)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert facade_factory.system_link_service_manager_facade.start_count == 1
    assert facade_factory.system_link_service_manager_facade.are_services_running


@pytest.mark.unit
def test_migrate_services_with_capture_action_does_not_restart_web_server():
    facade_factory = configure_fake_facade_factory()
    service = FakeMigrator()

    argument_handler = FakeArgumentHandler([service], MigrationAction.CAPTURE)
    service_migrator = MigrationFacilitator(facade_factory, argument_handler)
    service_migrator.migrate()

    assert facade_factory.ni_web_server_manager_facade.restart_count == 0


@pytest.mark.unit
def test_migrate_services_with_restore_action_restarts_web_server():
    facade_factory = configure_fake_facade_factory()
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
    pre_restore_count = 0
    pre_capture_count = 0
    fail_pre_check = False

    @property
    def help(self):
        return ''

    @property
    def name(self):
        return 'test'

    @property
    def argument(self):
        return 'test'

    def capture(self, migration_directory, facade_factory, arguments) -> None:
        self.capture_count += 1
        self.capture_migration_directory = migration_directory

    def restore(self, migration_directory, facade_factory, arguments) -> None:
        self.restore_count += 1
        self.restore_migration_directory = migration_directory

    def pre_capture_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        self.pre_capture_count += 1
        self.pre_capture_migration_directory = migration_directory
        if self.fail_pre_check:
            raise RuntimeError('pre capture failure')

    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        self.pre_restore_count += 1
        self.pre_restore_migration_directory = migration_directory
        if self.fail_pre_check:
            raise RuntimeError('pre restore failure')

    def is_service_installed(self, facade_factory: FacadeFactory) -> bool:
        return True


def configure_fake_facade_factory() -> FakeFacadeFactory:
    fake_facade_factory = FakeFacadeFactory()
    fake_facade_factory.file_system_facade.config = CONFIGURATION_FOR_TEST
    return fake_facade_factory
