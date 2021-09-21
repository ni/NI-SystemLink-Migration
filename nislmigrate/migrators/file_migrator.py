import os
from typing import Any, Dict

from nislmigrate.extensibility.migrator_plugin import MigratorPlugin, ArgumentManager
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.utility.paths import get_ni_application_data_directory_path

DEFAULT_DATA_DIRECTORY = os.path.join(
    get_ni_application_data_directory_path(),
    'Skyline',
    'Data',
    'FileIngestion')

PATH_CONFIGURATION_KEY = 'OutputPath'

S3_CONFIGURATION_KEY = 'UseS3BackEnd'

_METADATA_ONLY_ARGUMENT = 'metadata-only'

_METADATA_ONLY_HELP = 'When used with --files or --all, migrate only the file metadata, \
but not the files themselves. Otherwise ignored.'

_NO_FILES_ERROR = """

Files data was not found. If you intend to restore metadata only, pass
--files-metadata-only.

"""

_CANNOT_MIGRATE_S3_FILES_ERROR = """

S3 file storeage is enabled on the backend. nislmigrate cannot capture/restore the files
stored in S3. If you intend to migrate metadata only, pass --files-metadata-only.

"""


class _FileMigratorConfiguration:
    def __init__(
        self, migration_directory: str,
        facade_factory: FacadeFactory,
        arguments: Dict[str, Any],
        config: Dict[str, Any]
    ):
        self.mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        self.file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        self.mongo_configuration: MongoConfiguration = MongoConfiguration(config)
        self.file_migration_directory: str = os.path.join(migration_directory, 'files')
        self.file_migration_directory_exists: bool = self.file_facade.does_directory_exist(
                self.file_migration_directory)

        self.data_directory: str = config.get(PATH_CONFIGURATION_KEY) or DEFAULT_DATA_DIRECTORY

        self.is_s3_backend: bool = config.get(S3_CONFIGURATION_KEY, '').lower() == 'true'
        self.has_metadata_only_argument: bool = arguments.get(_METADATA_ONLY_ARGUMENT, False)
        self.should_migrate_files: bool = not self.has_metadata_only_argument


class FileMigrator(MigratorPlugin):

    @property
    def name(self):
        return 'FileIngestion'

    @property
    def argument(self):
        return 'files'

    @property
    def help(self):
        return 'Migrate ingested files'

    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        configuration = _FileMigratorConfiguration(
            migration_directory,
            facade_factory,
            arguments,
            self.config(facade_factory)
        )

        configuration.mongo_facade.capture_database_to_directory(
            configuration.mongo_configuration,
            migration_directory,
            self.name)

        if configuration.should_migrate_files:
            configuration.file_facade.copy_directory(
                configuration.data_directory,
                configuration.file_migration_directory,
                False)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        configuration = _FileMigratorConfiguration(
            migration_directory,
            facade_factory,
            arguments,
            self.config(facade_factory)
        )

        configuration.mongo_facade.restore_database_from_directory(
            configuration.mongo_configuration,
            migration_directory,
            self.name)

        if configuration.should_migrate_files:
            configuration.file_facade.copy_directory(
                configuration.file_migration_directory,
                configuration.data_directory,
                True)

    def pre_capture_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:

        configuration = _FileMigratorConfiguration(
            migration_directory,
            facade_factory,
            arguments,
            self.config(facade_factory)
        )

        if not configuration.has_metadata_only_argument and configuration.is_s3_backend:
            raise MigrationError(_CANNOT_MIGRATE_S3_FILES_ERROR)

    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:

        configuration = _FileMigratorConfiguration(
            migration_directory,
            facade_factory,
            arguments,
            self.config(facade_factory)
        )

        configuration.mongo_facade.validate_can_restore_database_from_directory(
            migration_directory,
            self.name)

        if configuration.is_s3_backend and not configuration.has_metadata_only_argument:
            raise MigrationError(_CANNOT_MIGRATE_S3_FILES_ERROR)
        elif not configuration.file_migration_directory_exists and configuration.should_migrate_files:
            raise MigrationError(_NO_FILES_ERROR)

    def add_additional_arguments(self, argument_manager: ArgumentManager):
        argument_manager.add_switch(_METADATA_ONLY_ARGUMENT, help=_METADATA_ONLY_HELP)
