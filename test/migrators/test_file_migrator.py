from typing import Optional
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.migrators.file_migrator import (
    FileMigrator,
    DEFAULT_DATA_DIRECTORY,
    PATH_CONFIGURATION_KEY,
    _METADATA_ONLY_ARGUMENT,
    _NO_FILES_ERROR
)
import pytest
from test.test_utilities import FakeFacadeFactory, FakeFileSystemFacade


@pytest.mark.unit
def test_file_migrator_captures_from_default_location_when_unconfigured():

    facade_factory = FakeFacadeFactory()
    file_system_facade = configure_fake_file_system_facade(facade_factory)
    migrator = FileMigrator()

    migrator.capture('data_dir', facade_factory, {})

    assert file_system_facade.last_from_directory == DEFAULT_DATA_DIRECTORY


@pytest.mark.unit
def test_file_migrator_captures_from_configured_location():

    facade_factory = FakeFacadeFactory()
    expected_directory = 'custom/directory'
    file_system_facade = configure_fake_file_system_facade(facade_factory, expected_directory=expected_directory)
    migrator = FileMigrator()

    migrator.capture('data_dir', facade_factory, {})

    assert file_system_facade.last_from_directory == expected_directory


@pytest.mark.unit
def test_file_migrator_restores_to_default_location_when_unconfigured():

    facade_factory = FakeFacadeFactory()
    file_system_facade = configure_fake_file_system_facade(facade_factory)
    migrator = FileMigrator()

    migrator.restore('data_dir', facade_factory, {})

    assert file_system_facade.last_to_directory == DEFAULT_DATA_DIRECTORY


@pytest.mark.unit
def test_file_migrator_restores_to_configured_location():

    facade_factory = FakeFacadeFactory()
    expected_directory = 'custom/directory'
    file_system_facade = configure_fake_file_system_facade(facade_factory, expected_directory=expected_directory)
    migrator = FileMigrator()

    migrator.restore('data_dir', facade_factory, {})

    assert file_system_facade.last_to_directory == expected_directory


@pytest.mark.unit
def test_file_migrator_does_not_capture_files_when_metadata_only_is_passed():

    facade_factory = FakeFacadeFactory()
    file_system_facade = configure_fake_file_system_facade(facade_factory)
    migrator = FileMigrator()

    migrator.capture('data_dir', facade_factory, {_METADATA_ONLY_ARGUMENT: True})

    assert file_system_facade.last_from_directory is None


@pytest.mark.unit
def test_file_migrator_does_not_restore_files_when_metadata_only_is_passed():

    facade_factory = FakeFacadeFactory()
    file_system_facade = configure_fake_file_system_facade(facade_factory, directory_exists=False)
    migrator = FileMigrator()

    migrator.restore('data_dir', facade_factory, {_METADATA_ONLY_ARGUMENT: True})

    assert file_system_facade.last_to_directory is None


@pytest.mark.unit
def test_file_migrator_reports_error_if_no_files_to_restore_and_not_metdata_only():

    facade_factory = FakeFacadeFactory()
    configure_fake_file_system_facade(facade_factory, directory_exists=False)
    migrator = FileMigrator()

    with pytest.raises(MigrationError) as e:
        migrator.pre_restore_check('data_dir', facade_factory, {})

    assert _NO_FILES_ERROR.strip() in e.exconly()


def configure_fake_file_system_facade(
    facade_factory: FakeFacadeFactory,
    directory_exists: bool = True,
    expected_directory: Optional[str] = None
) -> FakeFileSystemFacade:
    file_system_facade = facade_factory.file_system_facade
    file_system_facade.config = {
            'FileIngestion': {
                'Mongo.CustomConnectionString': 'mongodb://localhost',
                'Mongo.Database': 'file'
            }
        }
    file_system_facade.directory_exists = directory_exists

    if expected_directory is not None:
        file_system_facade.config['FileIngestion'][PATH_CONFIGURATION_KEY] = expected_directory

    return file_system_facade
