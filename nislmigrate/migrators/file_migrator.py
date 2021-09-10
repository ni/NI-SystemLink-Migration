import os

from nislmigrate.extensibility.migrator_plugin import MigratorPlugin, ArgumentManager
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.logs.migration_error import MigrationError
from typing import Any, Dict

DEFAULT_DATA_DIRECTORY = os.path.join(
    str(os.environ.get('ProgramData')),
    'National Instruments',
    'Skyline',
    'Data',
    'FileIngestion')

PATH_CONFIGURATION_KEY = 'OutputPath'

_METADATA_ONLY_ARGUMENT = 'metadata-only'

_METADATA_ONLY_HELP = 'When used with --files or --all, migrate only the file metadata, \
but not the files themselves. Otherwise ignored.'

_NO_FILES_ERROR = """

Files data was not found. If you intend to restore metadata only, pass
--files-metadata-only.

"""


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
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_migration_directory = os.path.join(migration_directory, 'files')

        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)

        if self.__should_migrate_files(arguments):
            file_facade.copy_directory(
                self.__data_directory(facade_factory),
                file_migration_directory,
                False)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_migration_directory = os.path.join(migration_directory, 'files')

        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)

        if self.__should_migrate_files(arguments):
            file_facade.copy_directory(
                file_migration_directory,
                self.__data_directory(facade_factory),
                True)

    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_database_from_directory(
            migration_directory,
            self.name)

        if self.__should_migrate_files(arguments):
            file_migration_directory = os.path.join(migration_directory, 'files')
            file_facade = facade_factory.get_file_system_facade()
            if not file_facade.migration_dir_exists(file_migration_directory):
                raise MigrationError(_NO_FILES_ERROR)

    def add_additional_arguments(self, argument_manager: ArgumentManager):
        argument_manager.add_switch(_METADATA_ONLY_ARGUMENT, help=_METADATA_ONLY_HELP)

    def __data_directory(self, facade_factory):
        return self.config(facade_factory).get(PATH_CONFIGURATION_KEY, DEFAULT_DATA_DIRECTORY)

    def __should_migrate_files(self, arguments):
        return not arguments.get(_METADATA_ONLY_ARGUMENT)
