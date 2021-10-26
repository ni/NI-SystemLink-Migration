from nislmigrate.logs.migration_error import MigrationError
import pytest

from nislmigrate.migrators.systems_management_migrator import SystemsManagementMigrator, \
    NO_SECRET_ERROR, \
    PKI_INSTALLED_PATH, \
    PILLAR_INSTALLED_PATH
from test.test_utilities import FakeFacadeFactory, FakeFileSystemFacade
from typing import Any, Dict, Tuple


@pytest.mark.unit
def test_systems_management_migrator_pre_capture_check():

    facade_factory, file_system_facade = configure_facade_factory()
    migrator = SystemsManagementMigrator()

    migrator.pre_capture_check('data_dir', facade_factory, {'secret': 'password'})


@pytest.mark.unit
def test_systems_management_migrator_pre_restore_check():

    facade_factory, file_system_facade = configure_facade_factory()
    migrator = SystemsManagementMigrator()

    migrator.pre_restore_check('data_dir', facade_factory, {'secret': 'password'})


@pytest.mark.unit
def test_systems_management_migrator_pre_capture_check_raises_when_secret_not_provided():

    facade_factory, file_system_facade = configure_facade_factory()
    migrator = SystemsManagementMigrator()

    with pytest.raises(MigrationError) as e:
        migrator.pre_capture_check('data_dir', facade_factory, {})
        assert e.value == NO_SECRET_ERROR


@pytest.mark.unit
def test_systems_management_migrator_pre_restore_check_raises_when_secret_not_provided():

    facade_factory, file_system_facade = configure_facade_factory()
    migrator = SystemsManagementMigrator()

    with pytest.raises(MigrationError) as e:
        migrator.pre_restore_check('data_dir', facade_factory, {})
        assert e.value == NO_SECRET_ERROR


@pytest.mark.unit
def test_systems_management_migrator_pre_restore_check_raises_when_salt_data_not_present():

    facade_factory, file_system_facade = configure_facade_factory()
    file_system_facade.missing_files.append('pki')
    migrator = SystemsManagementMigrator()

    with pytest.raises(FileNotFoundError):
        migrator.pre_restore_check('data_dir', facade_factory, {})


@pytest.mark.unit
def test_systems_management_migrator_capture_pki_files_captured():

    facade_factory, file_system_facade = configure_facade_factory()
    migrator = SystemsManagementMigrator()

    migrator.capture('data_dir', facade_factory, {'secret': 'password'})

    assert (PKI_INSTALLED_PATH, 'data_dir\\pki', 'password') in file_system_facade.directories_encrypted


@pytest.mark.unit
def test_systems_management_migrator_capture_pillar_files_captured():

    facade_factory, file_system_facade = configure_facade_factory()
    migrator = SystemsManagementMigrator()

    migrator.capture('data_dir', facade_factory, {'secret': 'password'})

    assert (PILLAR_INSTALLED_PATH, 'data_dir\\pillar', 'password') in file_system_facade.directories_encrypted


@pytest.mark.unit
def test_systems_management_migrator_capture_pillar_files_do_not_exist_and_are_not_captured():
    facade_factory, file_system_facade = configure_facade_factory()
    file_system_facade.missing_directories.append(PILLAR_INSTALLED_PATH)
    migrator = SystemsManagementMigrator()

    migrator.capture('data_dir', facade_factory, {'secret': 'password'})

    assert (PILLAR_INSTALLED_PATH, 'data_dir\\pillar', 'password') not in file_system_facade.directories_encrypted


def configure_facade_factory() -> Tuple[FakeFacadeFactory, FakeFileSystemFacade]:
    facade_factory = FakeFacadeFactory()
    file_system_facade = configure_fake_file_system_facade(facade_factory)
    return facade_factory, file_system_facade


def configure_fake_file_system_facade(facade_factory: FakeFacadeFactory) -> FakeFileSystemFacade:
    file_system_facade = facade_factory.file_system_facade
    properties: Dict[str, Any] = {
        'Mongo.CustomConnectionString': 'mongodb://localhost',
        'Mongo.Database': 'file'
    }
    file_system_facade.config = {
        'SystemsManagement': properties
    }
    return file_system_facade
