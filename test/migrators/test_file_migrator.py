from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.migrators.file_migrator import (
    FileMigrator,
    DEFAULT_DATA_DIRECTORY,
    PATH_CONFIGURATION_KEY,
    _METADATA_ONLY_ARGUMENT,
    _NO_FILES_ERROR,
    S3_CONFIGURATION_KEY,
    _CANNOT_MIGRATE_S3_FILES_ERROR,
)
import pytest
from test.test_utilities import FakeFacadeFactory
from typing import Any, Dict, Optional, Tuple


@pytest.mark.unit
@pytest.mark.parametrize('null_path', [(False), (True)])
def test_file_migrator_captures_from_default_location_when_unconfigured(null_path: bool):

    facade_factory, file_system_facade = configure_facade_factory(null_data_directory=null_path)
    migrator = FileMigrator()

    migrator.capture('data_dir', facade_factory, {})

    assert file_system_facade.last_from_directory == DEFAULT_DATA_DIRECTORY


@pytest.mark.unit
def test_file_migrator_captures_from_configured_location():

    expected_directory = 'custom/directory'
    facade_factory, file_system_facade = configure_facade_factory(data_directory=expected_directory)
    migrator = FileMigrator()

    migrator.capture('data_dir', facade_factory, {})

    assert file_system_facade.last_from_directory == expected_directory


@pytest.mark.unit
@pytest.mark.parametrize('null_path', [(False), (True)])
def test_file_migrator_restores_to_default_location_when_unconfigured(null_path: bool):

    facade_factory, file_system_facade = configure_facade_factory(null_data_directory=null_path)
    migrator = FileMigrator()

    migrator.restore('data_dir', facade_factory, {})

    assert file_system_facade.last_to_directory == DEFAULT_DATA_DIRECTORY


@pytest.mark.unit
def test_file_migrator_restores_to_configured_location():

    expected_directory = 'custom/directory'
    facade_factory, file_system_facade = configure_facade_factory(data_directory=expected_directory)
    migrator = FileMigrator()

    migrator.restore('data_dir', facade_factory, {})

    assert file_system_facade.last_to_directory == expected_directory


@pytest.mark.unit
def test_file_migrator_does_not_capture_files_when_metadata_only_is_passed():

    facade_factory, file_system_facade = configure_facade_factory()
    migrator = FileMigrator()

    migrator.capture('data_dir', facade_factory, {_METADATA_ONLY_ARGUMENT: True})

    assert file_system_facade.last_from_directory is None


@pytest.mark.unit
def test_file_migrator_does_not_restore_files_when_metadata_only_is_passed():

    facade_factory, file_system_facade = configure_facade_factory(dir_exists=False)
    migrator = FileMigrator()

    migrator.restore('data_dir', facade_factory, {_METADATA_ONLY_ARGUMENT: True})

    assert file_system_facade.last_to_directory is None


@pytest.mark.unit
@pytest.mark.parametrize('use_s3_backend', [(None), (False)])
def test_file_migrator_reports_error_if_no_files_to_restore_and_not_metdata_only(use_s3_backend):

    facade_factory, _ = configure_facade_factory(dir_exists=False, enable_s3_backend=use_s3_backend)
    migrator = FileMigrator()

    with pytest.raises(MigrationError) as e:
        migrator.pre_restore_check('data_dir', facade_factory, {})

    assert _NO_FILES_ERROR.strip() in e.exconly()


@pytest.mark.unit
def test_file_migrator_pre_capture_check_metadata_only_does_not_throw_when_s3_backend_is_enabled():
    facade_factory, _ = configure_facade_factory(enable_s3_backend=True)
    migrator = FileMigrator()

    migrator.pre_capture_check('data_dir', facade_factory, {_METADATA_ONLY_ARGUMENT: True})


@pytest.mark.unit
@pytest.mark.parametrize('use_s3_backend', [(None), (False)])
def test_file_migrator_pre_capture_check_metadata_does_not_throw_when_s3_backend_is_not_enabled(use_s3_backend):
    facade_factory, _ = configure_facade_factory(enable_s3_backend=use_s3_backend)
    migrator = FileMigrator()

    migrator.pre_capture_check('data_dir', facade_factory, {})


@pytest.mark.unit
def test_file_migrator_pre_restore_check_metadata_only_does_not_throw_when_s3_backend_is_enabled():
    facade_factory, _ = configure_facade_factory(enable_s3_backend=True)
    migrator = FileMigrator()

    migrator.pre_restore_check('data_dir', facade_factory, {_METADATA_ONLY_ARGUMENT: True})


@pytest.mark.unit
def test_file_migrator_pre_capture_check_reports_error_when_s3_backend_is_enabled_without_ignore_metadata_argument():
    facade_factory, _ = configure_facade_factory(enable_s3_backend=True)
    migrator = FileMigrator()

    with pytest.raises(MigrationError) as e:
        migrator.pre_capture_check('data_dir', facade_factory, {})

    assert _CANNOT_MIGRATE_S3_FILES_ERROR in str(e.value)


@pytest.mark.unit
def test_file_migrator_pre_restore_check_reports_error_when_s3_backend_is_enabled_without_ignore_metadata_argument():
    facade_factory, _ = configure_facade_factory(enable_s3_backend=True, dir_exists=False)
    migrator = FileMigrator()

    with pytest.raises(MigrationError) as e:
        migrator.pre_restore_check('data_dir', facade_factory, {})

    assert _CANNOT_MIGRATE_S3_FILES_ERROR in str(e.value)


class FakeFileSystemFacade(FileSystemFacade):
    def __init__(
        self,
        data_directory: Optional[str] = None,
        null_data_directory: bool = False,
        enable_s3_backend: Optional[bool] = None,
        dir_exists: bool = True,
    ):
        self.last_from_directory: Optional[str] = None
        self.last_to_directory: Optional[str] = None

        self.config: Dict[str, Any] = {
                'Mongo.CustomConnectionString': 'mongodb://localhost',
                'Mongo.Database': 'file'
            }

        if null_data_directory:
            self.config[PATH_CONFIGURATION_KEY] = None
        elif data_directory is not None:
            self.config[PATH_CONFIGURATION_KEY] = data_directory

        if enable_s3_backend is not None:
            self.config[S3_CONFIGURATION_KEY] = str(enable_s3_backend)

        self.dir_exists = dir_exists

    def copy_directory(self, from_directory: str, to_directory: str, force: bool):
        self.last_from_directory = from_directory
        self.last_to_directory = to_directory

    def read_json_file(self, path: str) -> dict:
        return {'FileIngestion': self.config}

    def migration_dir_exists(self, dir_):
        return self.dir_exists


def configure_facade_factory(
    data_directory: Optional[str] = None,
    null_data_directory: bool = False,
    enable_s3_backend: Optional[bool] = None,
    dir_exists: bool = True,
) -> Tuple[FakeFacadeFactory, FakeFileSystemFacade]:
    file_system_facade = FakeFileSystemFacade(
        data_directory=data_directory,
        null_data_directory=null_data_directory,
        enable_s3_backend=enable_s3_backend,
        dir_exists=dir_exists,
    )

    facade_factory = FakeFacadeFactory()
    facade_factory.file_system_facade = file_system_facade

    return (facade_factory, file_system_facade)
