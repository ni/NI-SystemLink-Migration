from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.migrators.file_migrator import FileMigrator, DEFAULT_DATA_DIRECTORY, PATH_CONFIGURATION_KEY, _METADATA_ONLY_ARGUMENT
import pytest
from test.test_utilities import FakeFacadeFactory
from typing import Optional


@pytest.mark.unit
def test_file_migrator_captures_from_default_location_when_unconfigured():

    facade_factory = FakeFacadeFactory()
    file_system_facade = FakeFileSystemFacade()
    facade_factory.file_system_facade = file_system_facade
    migrator = FileMigrator()

    migrator.capture('data_dir', facade_factory, {})

    assert file_system_facade.last_from_directory == DEFAULT_DATA_DIRECTORY


@pytest.mark.unit
def test_file_migrator_captures_from_configured_location():

    facade_factory = FakeFacadeFactory()
    file_system_facade = FakeFileSystemFacade()
    facade_factory.file_system_facade = file_system_facade
    migrator = FileMigrator()
    expected_directory = 'custom/directory'
    file_system_facade.config[PATH_CONFIGURATION_KEY] = expected_directory

    migrator.capture('data_dir', facade_factory, {})

    assert file_system_facade.last_from_directory == expected_directory


@pytest.mark.unit
def test_file_migrator_restores_to_default_location_when_unconfigured():

    facade_factory = FakeFacadeFactory()
    file_system_facade = FakeFileSystemFacade()
    facade_factory.file_system_facade = file_system_facade
    migrator = FileMigrator()

    migrator.restore('data_dir', facade_factory, {})

    assert file_system_facade.last_to_directory == DEFAULT_DATA_DIRECTORY


@pytest.mark.unit
def test_file_migrator_restores_to_configured_location():

    facade_factory = FakeFacadeFactory()
    file_system_facade = FakeFileSystemFacade()
    facade_factory.file_system_facade = file_system_facade
    migrator = FileMigrator()
    expected_directory = 'custom/directory'
    file_system_facade.config[PATH_CONFIGURATION_KEY] = expected_directory

    migrator.restore('data_dir', facade_factory, {})

    assert file_system_facade.last_to_directory == expected_directory


@pytest.mark.unit
def test_file_migrator_does_not_capture_files_when_metadata_only_is_passed():

    facade_factory = FakeFacadeFactory()
    file_system_facade = FakeFileSystemFacade()
    facade_factory.file_system_facade = file_system_facade
    migrator = FileMigrator()
    expected_directory = 'custom/directory'

    migrator.capture('data_dir', facade_factory, {_METADATA_ONLY_ARGUMENT: True})

    assert file_system_facade.last_from_directory == None


@pytest.mark.unit
def test_file_migrator_does_not_restore_files_when_metadata_only_is_passed():

    facade_factory = FakeFacadeFactory()
    file_system_facade = FakeFileSystemFacade()
    facade_factory.file_system_facade = file_system_facade
    migrator = FileMigrator()
    expected_directory = 'custom/directory'

    migrator.restore('data_dir', facade_factory, {_METADATA_ONLY_ARGUMENT: True})

    assert file_system_facade.last_to_directory == None


class FakeFileSystemFacade(FileSystemFacade):
    def __init__(self):
        self.last_from_directory: Optional[str] = None
        self.last_to_directory: Optional[str] = None

        self.config = {
                'Mongo.CustomConnectionString': 'mongodb://localhost',
                'Mongo.Database': 'file'
            }

    def copy_directory(self, from_directory: str, to_directory: str, force: bool):
        self.last_from_directory = from_directory
        self.last_to_directory = to_directory

    def read_json_file(self, path: str) -> dict:
        return {'FileIngestion': self.config}
